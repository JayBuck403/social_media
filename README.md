# Edify! - Hobby Social Feed

Minimal Flask API plus static frontend to bring the project to life.

## Run locally

1. Install Python 3.9+ and pip.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the server (port 8000 recommended if 5000 is busy):
   ```bash
   PORT=8000 python app.py
   ```
4. Open the app at:
   - http://localhost:8000/

## API quickstart (legacy FileStorage)

- Health: `GET /api/health`
- List all: `GET /api/objects`
- List by class: `GET /api/Post` (also `User`, `Comment`, `Likes`)
- Create: `POST /api/Post` JSON body, e.g. `{ "text": "Hello", "user_id": "u1" }`
- Get one: `GET /api/Post/<id>`
- Update: `PUT /api/Post/<id>` JSON body with fields to change
- Delete: `DELETE /api/Post/<id>`

Data persists to `file.json` using the existing `FileStorage` engine.

## New REST endpoints (SQLAlchemy, SQLite)

- Create user: `POST /users` body `{ email, first_name, last_name }`
- List users: `GET /users`
- Create post: `POST /posts` body `{ text, user_id }`
- List posts: `GET /posts`
- Post by id: `GET /posts/:id`
- Update post: `PUT /posts/:id`
- Delete post: `DELETE /posts/:id`
- Comments: `POST/GET /posts/:post_id/comments`
- Likes: `POST/GET /posts/:post_id/likes`

DB: SQLite at `/workspace/app.db`. Tables auto-create on startup.

### Seed data

```bash
python seed.py
```

