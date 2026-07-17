"""Local models endpoint."""

from flask import Blueprint, jsonify, request
import os
import json

bp = Blueprint("models", __name__)


@bp.route("/models", methods=["GET"])
def get_models():
    """Get list of available local models."""
    try:
        # This would typically query Ollama or local model storage
        # For now, returning a mock response
        models = [
            {"name": "qwen3:8b", "size": "5GB", "description": "Fast model for quick tasks"},
            {"name": "qwen3:14b", "size": "9GB", "description": "Good balance of speed and performance"},
            {"name": "qwen3-coder:30b", "size": "19GB", "description": "MoE model optimized for tool-use"}
        ]
        return jsonify({"models": models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/models/<model_name>", methods=["GET"])
def get_model_info(model_name):
    """Get detailed information about a specific model."""
    try:
        # Mock implementation - in reality this would query Ollama
        model_info = {
            "name": model_name,
            "size": "5-19GB",
            "description": "Qwen3-Coder model for local coding tasks",
            "context_window": "256K tokens",
            "languages": ["Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "C++"],
            "features": ["Code generation", "Multi-file editing", "Tool calling", "Agentic workflows"]
        }
        return jsonify({"model": model_info})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/models/<model_name>/status", methods=["GET"])
def get_model_status(model_name):
    """Get status of a specific model."""
    try:
        # Mock implementation
        status = {
            "name": model_name,
            "loaded": True,
            "size": "5-19GB",
            "last_used": "2023-01-01T00:00:00Z"
        }
        return jsonify({"status": status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/models/<model_name>/load", methods=["POST"])
def load_model(model_name):
    """Load a model into memory."""
    try:
        # Mock implementation - in reality this would call Ollama
        data = request.get_json() or {}
        return jsonify({
            "message": f"Model {model_name} loading...",
            "status": "loading",
            "details": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/models/<model_name>/unload", methods=["POST"])
def unload_model(model_name):
    """Unload a model from memory."""
    try:
        # Mock implementation
        return jsonify({
            "message": f"Model {model_name} unloaded",
            "status": "unloaded"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/models/switch", methods=["POST"])
def switch_model():
    """Switch between different models."""
    try:
        data = request.get_json()
        if not data or "model" not in data:
            return jsonify({"error": "Model name required"}), 400
        
        new_model = data["model"]
        # Mock implementation
        return jsonify({
            "message": f"Switched to model {new_model}",
            "status": "switched",
            "new_model": new_model
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
