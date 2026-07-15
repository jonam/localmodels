"""Shared validation helpers for route modules."""

from flask import jsonify, request


def require_json(*fields):
    """Validate that request has JSON body with required fields.
    Returns (data, None) on success or (None, error_response) on failure."""
    data = request.get_json()
    if not data:
        return None, (jsonify({"error": "JSON body required"}), 400)
    missing = [f for f in fields if f not in data]
    if missing:
        return None, (jsonify({"error": f"missing fields: {missing}"}), 400)
    return data, None
