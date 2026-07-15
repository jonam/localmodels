"""Tests for the palindrome route."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app


def test_palindrome_true():
    app = create_app()
    with app.test_client() as client:
        resp = client.post("/palindrome", json={"text": "racecar"})
        assert resp.status_code == 200
        assert resp.get_json()["is_palindrome"] is True


def test_palindrome_false():
    app = create_app()
    with app.test_client() as client:
        resp = client.post("/palindrome", json={"text": "hello"})
        assert resp.status_code == 200
        assert resp.get_json()["is_palindrome"] is False


def test_palindrome_missing_field():
    app = create_app()
    with app.test_client() as client:
        resp = client.post("/palindrome", json={})
        assert resp.status_code == 400
