#!/usr/bin/env python3
"""Seed the database with a demo user and posts."""

from database import SessionLocal, Base, engine
from models.sa_models import User, Post


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create a demo user if not exists
    user = db.query(User).filter(User.email == "demo@example.com").first()
    if not user:
        user = User(email="demo@example.com", first_name="Demo", last_name="User")
        db.add(user)
        db.commit()
        db.refresh(user)

    # Seed a couple of posts
    if db.query(Post).count() == 0:
        db.add_all([
            Post(text="Welcome to Edify!", user_id=user.id),
            Post(text="This is a seeded post.", user_id=user.id),
        ])
        db.commit()

    print("Seeding complete.")


if __name__ == "__main__":
    main()

