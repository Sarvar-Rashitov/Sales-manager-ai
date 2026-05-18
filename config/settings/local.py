"""
Local development settings — uses SQLite3, debug on, relaxed security.
"""
from .base import *  # noqa
import os
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env")  # noqa: F405

DEBUG = True

ALLOWED_HOSTS = ["*"]

# --- SQLite3 for local dev ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# --- CORS ---
CORS_ALLOW_ALL_ORIGINS = True

# --- Email (print to console) ---
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# --- Django Debug Toolbar (optional) ---
INTERNAL_IPS = ["127.0.0.1"]

# --- Override secrets from .env ---
SECRET_KEY = os.environ.get("SECRET_KEY", "local-dev-secret-key-not-for-production")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
TELEGRAM_API_ID = os.environ.get("TELEGRAM_API_ID", "")
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
