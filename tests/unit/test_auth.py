"""Unit tests for backend/auth.py.

These exercise the pure functions with no network or database. They are
the first line of defence against regressions in password hashing and
JWT handling.
"""
import time
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from auth import (
    ALGORITHM,
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from config import SECRET_KEY


class TestPasswordHashing:
    def test_hash_returns_salt_and_digest(self):
        h = hash_password("correct horse battery staple")
        salt, digest = h.split("$", 1)
        assert len(salt) == 32, "salt should be 16 bytes hex encoded"
        assert len(digest) == 64, "sha256 digest should be 32 bytes hex encoded"

    def test_same_password_hashes_to_different_values(self):
        a = hash_password("same-password")
        b = hash_password("same-password")
        assert a != b, "each hash must use a fresh random salt"

    def test_verify_correct_password(self):
        h = hash_password("s3cret!")
        assert verify_password("s3cret!", h) is True

    def test_verify_wrong_password(self):
        h = hash_password("s3cret!")
        assert verify_password("not-the-right-one", h) is False

    def test_verify_malformed_hash_returns_false(self):
        assert verify_password("any", "not-a-valid-hash") is False

    def test_verify_empty_hash_returns_false(self):
        assert verify_password("any", "") is False

    def test_verify_handles_unicode_password(self):
        pw = "pässwörd😀"
        assert verify_password(pw, hash_password(pw)) is True


class TestJwt:
    def test_roundtrip_encode_decode(self):
        token = create_access_token({"sub": "alice@example.com", "name": "Alice"})
        payload = decode_token(token)
        assert payload["sub"] == "alice@example.com"
        assert payload["name"] == "Alice"
        assert "exp" in payload

    def test_invalid_token_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            decode_token("this.is.not.a.jwt")
        assert exc.value.status_code == 401

    def test_tampered_signature_raises_401(self):
        token = create_access_token({"sub": "alice"})
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        with pytest.raises(HTTPException) as exc:
            decode_token(tampered)
        assert exc.value.status_code == 401

    def test_expired_token_raises_401(self):
        expired_payload = {
            "sub": "alice",
            "exp": datetime.utcnow() - timedelta(hours=1),
        }
        expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
        with pytest.raises(HTTPException) as exc:
            decode_token(expired_token)
        assert exc.value.status_code == 401

    def test_token_uses_configured_algorithm(self):
        token = create_access_token({"sub": "bob"})
        header_b64, _, _ = token.split(".")
        # jose does not expose header directly; decode unverified to inspect.
        payload = jwt.get_unverified_header(token)
        assert payload["alg"] == ALGORITHM
