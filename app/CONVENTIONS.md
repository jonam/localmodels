# Project Conventions

This is a Flask application. All routes use Flask blueprints.

## Route module pattern

Every file in routes/ MUST follow this exact structure:

```python
"""Short description of the route."""

from flask import Blueprint, jsonify, request

bp = Blueprint("<name>", __name__)


@bp.route("/<path>", methods=["POST"])
def handler_name():
    data = request.get_json()
    if not data or "field" not in data:
        return jsonify({"error": "missing 'field' field"}), 400

    # logic here

    return jsonify({"result": value})
```

## Rules

- Framework: Flask (NOT FastAPI, NOT Django, NOT Express)
- Every route file exports `bp` (a Blueprint)
- Use `request.get_json()` for POST body
- Return `jsonify(...)` with appropriate status codes
- Validate input, return 400 on bad input
- Shared utilities go in shared/ and are imported as `from shared.module import func`
