"""Unit tests for backend/config.py helpers."""
import pytest

from config import _required


def test_required_returns_value_when_set(monkeypatch):
    monkeypatch.setenv("RUDRA_TEST_VAR", "hello")
    assert _required("RUDRA_TEST_VAR") == "hello"


def test_required_exits_when_missing(monkeypatch):
    monkeypatch.delenv("RUDRA_TEST_VAR", raising=False)
    with pytest.raises(SystemExit) as exc:
        _required("RUDRA_TEST_VAR")
    assert exc.value.code == 1


def test_required_exits_when_empty_string(monkeypatch):
    """An empty env var is just as dangerous as a missing one."""
    monkeypatch.setenv("RUDRA_TEST_VAR", "")
    with pytest.raises(SystemExit) as exc:
        _required("RUDRA_TEST_VAR")
    assert exc.value.code == 1
