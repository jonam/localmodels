"""Flask app that auto-registers all blueprints from routes/."""

import importlib
import os
from flask import Flask


def create_app():
    app = Flask(__name__)

    routes_dir = os.path.join(os.path.dirname(__file__), "routes")
    for fname in sorted(os.listdir(routes_dir)):
        if fname.endswith(".py") and not fname.startswith("_"):
            module_name = fname[:-3]
            mod = importlib.import_module(f"routes.{module_name}")
            if hasattr(mod, "bp"):
                app.register_blueprint(mod.bp)

    return app


if __name__ == "__main__":
    app = create_app()
    print("Routes:", [rule.rule for rule in app.url_map.iter_rules() if rule.rule != "/static/<path:filename>"])
    app.run(debug=True, port=8000)
