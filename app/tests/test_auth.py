"""
Tests for auth — JWT creation, password hashing, RBAC access control.
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPasswordHashing:
    def test_hash_and_verify(self):
        from app.api.core.security import hash_password, verify_password
        hashed = hash_password("mysecretpass")
        assert hashed != "mysecretpass"
        assert verify_password("mysecretpass", hashed)

    def test_wrong_password_fails(self):
        from app.api.core.security import hash_password, verify_password
        hashed = hash_password("correctpass")
        assert not verify_password("wrongpass", hashed)

    def test_hash_is_different_each_time(self):
        from app.api.core.security import hash_password
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # bcrypt uses random salt


class TestJWT:
    def test_create_and_decode(self):
        from app.api.core.security import create_access_token, decode_token
        token = create_access_token({"sub": "testuser", "role": "admin", "user_id": 1})
        payload = decode_token(token)
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert payload["user_id"] == 1

    def test_invalid_token_raises(self):
        from app.api.core.security import decode_token
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_tampered_token_raises(self):
        from app.api.core.security import create_access_token, decode_token
        from fastapi import HTTPException
        token = create_access_token({"sub": "user"})
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException):
            decode_token(tampered)


class TestRBAC:
    def test_admin_gets_all_levels(self):
        from app.rag.guardrails.access_control import get_allowed_access_levels
        levels = get_allowed_access_levels("admin")
        assert "hr" in levels
        assert "engineering" in levels
        assert "sales" in levels
        assert "public" in levels

    def test_hr_only_gets_hr_and_public(self):
        from app.rag.guardrails.access_control import get_allowed_access_levels
        levels = get_allowed_access_levels("hr")
        assert "hr" in levels
        assert "public" in levels
        assert "engineering" not in levels
        assert "sales" not in levels

    def test_employee_only_gets_public(self):
        from app.rag.guardrails.access_control import get_allowed_access_levels
        levels = get_allowed_access_levels("employee")
        assert levels == ["public"]

    def test_unknown_role_defaults_to_public(self):
        from app.rag.guardrails.access_control import get_allowed_access_levels
        levels = get_allowed_access_levels("unknown_role")
        assert "public" in levels
        assert "hr" not in levels

    def test_can_access_document(self):
        from app.rag.guardrails.access_control import can_access_document
        assert can_access_document("admin", "hr") is True
        assert can_access_document("hr", "hr") is True
        assert can_access_document("employee", "hr") is False
        assert can_access_document("engineering", "hr") is False

    def test_admin_filter_is_none(self):
        from app.rag.guardrails.access_control import build_chroma_filter
        assert build_chroma_filter("admin") is None  # No filter needed

    def test_employee_filter(self):
        from app.rag.guardrails.access_control import build_chroma_filter
        f = build_chroma_filter("employee")
        assert f == {"access_level": {"$eq": "public"}}

    def test_hr_filter_uses_in(self):
        from app.rag.guardrails.access_control import build_chroma_filter
        f = build_chroma_filter("hr")
        assert "$in" in f["access_level"]
        assert "hr" in f["access_level"]["$in"]
        assert "public" in f["access_level"]["$in"]
