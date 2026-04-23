"""Shared pytest configuration.

Populates the environment variables that `backend/config.py` marks as
required so backend modules can be imported during tests without the
process exiting. Individual tests may override these via `monkeypatch`.
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))
sys.path.insert(0, str(REPO_ROOT / "sdk" / "python"))

os.environ.setdefault("KEYCLOAK_URL", "http://localhost:8080")
os.environ.setdefault("KEYCLOAK_EXTERNAL_URL", "http://localhost:8080")
os.environ.setdefault("KEYCLOAK_ADMIN_USER", "test-admin")
os.environ.setdefault("KEYCLOAK_ADMIN_PASSWORD", "test-admin-password")
os.environ.setdefault("MONGODB_URL", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DB", "rudra_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SECRET_KEY", "test-only-secret-key-never-deploy-this")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
