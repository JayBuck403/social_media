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

# SQLAlchemy imports
from database import Base, engine, SessionLocal
from models.sa_models import User as SAUser, Post as SAPost, Comment as SAComment, Like as SALike


def create_app() -> Flask:
    app = Flask(__name__, static_folder="web_static", static_url_path="")
    CORS(app)

    # Create DB tables if they do not exist
    Base.metadata.create_all(bind=engine)

    @app.teardown_appcontext
    def remove_session(exception=None):
        SessionLocal.remove()

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

    # ---------- New RESTful Endpoints (SQLAlchemy) ----------
    def serialize_user(u: SAUser):
        return {
            "id": u.id,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "updated_at": u.updated_at.isoformat() if u.updated_at else None,
        }

    def serialize_post(p: SAPost):
        return {
            "id": p.id,
            "text": p.text,
            "user_id": p.user_id,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }

    def serialize_comment(c: SAComment):
        return {
            "id": c.id,
            "comment": c.comment,
            "user_id": c.user_id,
            "post_id": c.post_id,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }

    def serialize_like(l: SALike):
        return {
            "id": l.id,
            "user_id": l.user_id,
            "post_id": l.post_id,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }

    # Users
    @app.route("/users", methods=["POST"])
    def create_user():
        payload = request.get_json(silent=True) or {}
        db = SessionLocal()
        user = SAUser(
            email=payload.get("email"),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return jsonify(serialize_user(user)), 201

    @app.route("/users", methods=["GET"])
    def list_users():
        db = SessionLocal()
        users = db.query(SAUser).all()
        return jsonify([serialize_user(u) for u in users])

    # Posts
    @app.route("/posts", methods=["POST"])
    def create_post():
        payload = request.get_json(silent=True) or {}
        db = SessionLocal()
        post = SAPost(text=payload.get("text"), user_id=payload.get("user_id"))
        db.add(post)
        db.commit()
        db.refresh(post)
        return jsonify(serialize_post(post)), 201

    @app.route("/posts", methods=["GET"])
    def list_posts():
        db = SessionLocal()
        posts = db.query(SAPost).order_by(SAPost.created_at.desc()).all()
        return jsonify([serialize_post(p) for p in posts])

    @app.route("/posts/<post_id>", methods=["GET"])
    def get_post(post_id):
        db = SessionLocal()
        post = db.get(SAPost, post_id)
        if not post:
            abort(404)
        return jsonify(serialize_post(post))

    @app.route("/posts/<post_id>", methods=["PUT"])
    def update_post(post_id):
        db = SessionLocal()
        post = db.get(SAPost, post_id)
        if not post:
            abort(404)
        payload = request.get_json(silent=True) or {}
        if "text" in payload:
            post.text = payload["text"]
        if "user_id" in payload:
            post.user_id = payload["user_id"]
        db.commit()
        db.refresh(post)
        return jsonify(serialize_post(post))

    @app.route("/posts/<post_id>", methods=["DELETE"])
    def delete_post(post_id):
        db = SessionLocal()
        post = db.get(SAPost, post_id)
        if not post:
            abort(404)
        db.delete(post)
        db.commit()
        return ("", 204)

    # Comments
    @app.route("/posts/<post_id>/comments", methods=["POST"])
    def create_comment(post_id):
        payload = request.get_json(silent=True) or {}
        db = SessionLocal()
        comment = SAComment(comment=payload.get("comment"), user_id=payload.get("user_id"), post_id=post_id)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return jsonify(serialize_comment(comment)), 201

    @app.route("/posts/<post_id>/comments", methods=["GET"])
    def list_comments(post_id):
        db = SessionLocal()
        comments = db.query(SAComment).filter(SAComment.post_id == post_id).order_by(SAComment.created_at.desc()).all()
        return jsonify([serialize_comment(c) for c in comments])

    # Likes
    @app.route("/posts/<post_id>/likes", methods=["POST"])
    def like_post(post_id):
        payload = request.get_json(silent=True) or {}
        db = SessionLocal()
        like = SALike(user_id=payload.get("user_id"), post_id=post_id)
        db.add(like)
        db.commit()
        db.refresh(like)
        return jsonify(serialize_like(like)), 201

    @app.route("/posts/<post_id>/likes", methods=["GET"])
    def list_likes(post_id):
        db = SessionLocal()
        likes = db.query(SALike).filter(SALike.post_id == post_id).all()
        return jsonify([serialize_like(l) for l in likes])

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

