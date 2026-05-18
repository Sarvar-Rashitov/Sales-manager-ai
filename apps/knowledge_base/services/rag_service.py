"""
RAG Service — document ingestion, chunking, FAISS indexing, and retrieval.

Pipeline:
  Upload → Extract Text → Chunk → Embed → FAISS Index → Retrieve → AI Response
"""
import os
import logging
import numpy as np
from pathlib import Path
from django.conf import settings
from apps.accounts.models import Organization
from apps.ai_agents.services.openai_client import get_embedding
from ..models import Document, DocumentChunk

logger = logging.getLogger("apps.knowledge_base")

FAISS_DIR = Path(settings.FAISS_INDEX_DIR)
FAISS_DIR.mkdir(parents=True, exist_ok=True)


def _get_faiss_path(org_id: str) -> Path:
    return FAISS_DIR / f"org_{org_id}.faiss"


def _get_meta_path(org_id: str) -> Path:
    return FAISS_DIR / f"org_{org_id}_meta.npy"


class RAGService:

    @staticmethod
    def ingest_document(document: Document) -> bool:
        """Full pipeline: extract → chunk → embed → index."""
        try:
            document.status = Document.Status.PROCESSING
            document.save(update_fields=["status"])

            text = RAGService._extract_text(document)
            if not text:
                raise ValueError("Could not extract text from document.")

            chunks = RAGService._chunk_text(text)
            RAGService._embed_and_index(document, chunks)

            document.status = Document.Status.READY
            document.chunk_count = len(chunks)
            document.save(update_fields=["status", "chunk_count"])
            logger.info("Document ingested: %s (%d chunks)", document.title, len(chunks))
            return True

        except Exception as e:
            document.status = Document.Status.FAILED
            document.error_message = str(e)
            document.save(update_fields=["status", "error_message"])
            logger.error("Document ingestion failed [%s]: %s", document.title, e)
            return False

    @staticmethod
    def _extract_text(document: Document) -> str:
        if document.doc_type == Document.DocType.URL:
            return RAGService._fetch_url(document.url)
        elif document.doc_type == Document.DocType.PDF:
            return RAGService._extract_pdf(document.file.path)
        elif document.doc_type == Document.DocType.DOCX:
            return RAGService._extract_docx(document.file.path)
        elif document.doc_type == Document.DocType.TXT:
            with open(document.file.path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        return ""

    @staticmethod
    def _extract_pdf(path: str) -> str:
        try:
            import pypdf
            reader = pypdf.PdfReader(path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            logger.warning("pypdf not installed. Install with: pip install pypdf")
            return ""

    @staticmethod
    def _extract_docx(path: str) -> str:
        try:
            import docx
            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            logger.warning("python-docx not installed. Install with: pip install python-docx")
            return ""

    @staticmethod
    def _fetch_url(url: str) -> str:
        try:
            import requests
            from bs4 import BeautifulSoup
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            logger.error("URL fetch error: %s", e)
            return ""

    @staticmethod
    def _chunk_text(text: str) -> list[str]:
        """Split text into overlapping chunks."""
        chunk_size = settings.CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i: i + chunk_size])
            chunks.append(chunk)
            i += chunk_size - overlap
        return [c for c in chunks if len(c.strip()) > 50]

    @staticmethod
    def _embed_and_index(document: Document, chunks: list[str]) -> None:
        """Embed chunks and add to FAISS index."""
        try:
            import faiss
        except ImportError:
            logger.warning("faiss-cpu not installed. Install with: pip install faiss-cpu")
            return

        org_id = str(document.organization_id)
        faiss_path = _get_faiss_path(org_id)
        meta_path = _get_meta_path(org_id)

        # Load or create index
        dim = 1536  # text-embedding-3-small dimension
        if faiss_path.exists():
            index = faiss.read_index(str(faiss_path))
            meta = list(np.load(str(meta_path), allow_pickle=True))
        else:
            index = faiss.IndexFlatL2(dim)
            meta = []

        # Delete old chunks for this document
        DocumentChunk.objects.filter(document=document).delete()

        embeddings = []
        chunk_objects = []

        for i, chunk_text in enumerate(chunks):
            embedding = get_embedding(chunk_text)
            if not embedding:
                continue
            faiss_id = index.ntotal + len(embeddings)
            embeddings.append(embedding)
            meta.append({"chunk_id": None, "doc_id": str(document.id), "text": chunk_text[:500]})
            chunk_objects.append(DocumentChunk(
                document=document,
                chunk_index=i,
                text=chunk_text,
                faiss_id=faiss_id,
            ))

        if embeddings:
            vectors = np.array(embeddings, dtype=np.float32)
            index.add(vectors)
            faiss.write_index(index, str(faiss_path))
            np.save(str(meta_path), np.array(meta, dtype=object))

        DocumentChunk.objects.bulk_create(chunk_objects)

    @staticmethod
    def search(organization: Organization, query: str, top_k: int = 5) -> list[str]:
        """Semantic search — returns top_k relevant text chunks."""
        try:
            import faiss
        except ImportError:
            return []

        org_id = str(organization.id)
        faiss_path = _get_faiss_path(org_id)
        meta_path = _get_meta_path(org_id)

        if not faiss_path.exists():
            return []

        query_embedding = get_embedding(query)
        if not query_embedding:
            return []

        index = faiss.read_index(str(faiss_path))
        meta = list(np.load(str(meta_path), allow_pickle=True))

        query_vec = np.array([query_embedding], dtype=np.float32)
        distances, indices = index.search(query_vec, top_k)

        results = []
        for idx in indices[0]:
            if 0 <= idx < len(meta):
                results.append(meta[idx].get("text", ""))

        return [r for r in results if r]
