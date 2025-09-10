#!/usr/bin/env python3
"""Minimal Flask API to breathe life into the hobby project.

Exposes CRUD-style endpoints backed by the existing FileStorage engine and
serves the static frontend under /.
"""

from flask import Flask, jsonify, request, send_from_directory, abort
from flask_cors import CORS
import os

from models import storage
from models.user import User
from models.post import Post
from models.comment import Comment
from models.likes import Likes


def create_app() -> Flask:
    app = Flask(__name__, static_folder="web_static", static_url_path="")
    CORS(app)

    # ---------- Helpers ----------
    def serialize_all():
        return {key: obj.to_dict() for key, obj in storage.all().items()}

    def get_by_class(cls_name: str):
        return {
            key: obj.to_dict()
            for key, obj in storage.all().items()
            if key.startswith(f"{cls_name}.")
        }

    def instantiate_from_class_name(class_name: str, payload: dict):
        class_map = {
            "User": User,
            "Post": Post,
            "Comment": Comment,
            "Likes": Likes,
        }
        if class_name not in class_map:
            abort(400, description="Unknown class")
        # Always instantiate without kwargs to avoid BaseModel kwargs-parsing branch
        instance = class_map[class_name]()
        for k, v in (payload or {}).items():
            if k not in {"id", "created_at", "updated_at", "__class__"}:
                setattr(instance, k, v)
        instance.save()
        return instance

    # ---------- Routes ----------
    @app.route("/api/health", methods=["GET"]) 
    def health():
        return jsonify({"status": "ok"})

    @app.route("/api/objects", methods=["GET"]) 
    def list_all():
        return jsonify(serialize_all())

    @app.route("/api/<class_name>", methods=["GET"]) 
    def list_by_class(class_name):
        return jsonify(get_by_class(class_name))

    @app.route("/api/<class_name>", methods=["POST"]) 
    def create_object(class_name):
        payload = request.get_json(silent=True) or {}
        instance = instantiate_from_class_name(class_name, payload)
        return jsonify(instance.to_dict()), 201

    @app.route("/api/<class_name>/<obj_id>", methods=["GET"]) 
    def get_object(class_name, obj_id):
        key = f"{class_name}.{obj_id}"
        obj = storage.all().get(key)
        if not obj:
            abort(404)
        return jsonify(obj.to_dict())

    @app.route("/api/<class_name>/<obj_id>", methods=["PUT"]) 
    def update_object(class_name, obj_id):
        key = f"{class_name}.{obj_id}"
        obj = storage.all().get(key)
        if not obj:
            abort(404)
        payload = request.get_json(silent=True) or {}
        # Protect core fields
        payload.pop("id", None)
        payload.pop("created_at", None)
        payload.pop("updated_at", None)
        for k, v in payload.items():
            setattr(obj, k, v)
        obj.save()
        return jsonify(obj.to_dict())

    @app.route("/api/<class_name>/<obj_id>", methods=["DELETE"]) 
    def delete_object(class_name, obj_id):
        key = f"{class_name}.{obj_id}"
        obj = storage.all().pop(key, None)
        if not obj:
            abort(404)
        # Persist removal
        storage.save()
        return ("", 204)

    # Serve index
    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "social.html")

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

