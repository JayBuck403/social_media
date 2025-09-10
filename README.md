# Edify! - Hobby Social Feed

Minimal Flask API plus static frontend to bring the project to life.

## Run locally

1. Install Python 3.9+ and pip.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the server:
   ```bash
   python app.py
   ```
4. Open the app at:
   - http://localhost:5000/

## API quickstart

- Health: `GET /api/health`
- List all: `GET /api/objects`
- List by class: `GET /api/Post` (also `User`, `Comment`, `Likes`)
- Create: `POST /api/Post` JSON body, e.g. `{ "text": "Hello", "user_id": "u1" }`
- Get one: `GET /api/Post/<id>`
- Update: `PUT /api/Post/<id>` JSON body with fields to change
- Delete: `DELETE /api/Post/<id>`

Data persists to `file.json` using the existing `FileStorage` engine.

