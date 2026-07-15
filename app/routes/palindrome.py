"""Check if a string is a palindrome."""

from flask import Blueprint, jsonify, request

bp = Blueprint("palindrome", __name__)


@bp.route("/palindrome", methods=["POST"])
def check_palindrome():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "missing 'text' field"}), 400

    text = data["text"]
    cleaned = "".join(c.lower() for c in text if c.isalnum())
    is_palindrome = cleaned == cleaned[::-1]

    return jsonify({"text": text, "is_palindrome": is_palindrome})
