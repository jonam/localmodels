"""Reverses a given text."""

from flask import Blueprint, jsonify, request

bp = Blueprint("reverse", __name__)

@bp.route("/reverse", methods=["POST"])
def reverse_text():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "missing 'text' field"}), 400

    reversed_text = data["text"][::-1]

    return jsonify({"reversed": reversed_text})
