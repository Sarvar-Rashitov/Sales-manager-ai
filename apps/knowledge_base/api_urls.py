from django.urls import path
from . import api_views

urlpatterns = [
    path("search/", api_views.search_api, name="api_kb_search"),
    path("documents/", api_views.document_list_api, name="api_kb_docs"),
]
