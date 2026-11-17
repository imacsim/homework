import os
import json
import itertools
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

FILE_PATH = "notes.json"


def load_notes():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_notes():
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


notes = load_notes()
max_id = max((n["id"] for n in notes), default=0)
note_ids = itertools.count(max_id + 1)


def find_note(note_id):
    return next((n for n in notes if n["id"] == note_id), None)


def is_valid_str(val):
    return isinstance(val, str) and bool(val.strip())


@app.get("/")
def index():
    return "<h1>Гостевая книга v3</h1>"


@app.get("/notes")
def list_notes():
    author = request.args.get("author")
    limit_str = request.args.get("limit", "10")
    offset_str = request.args.get("offset", "0")
    sort_field = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    if sort_field not in ("id", "likes"):
        return jsonify(error="sort must be 'id' or 'likes'"), 400
    if order not in ("asc", "desc"):
        return jsonify(error="order must be 'asc' or 'desc'"), 400

    try:
        limit = int(limit_str)
        offset = int(offset_str)
    except ValueError:
        return jsonify(error="limit and offset must be integers"), 400

    if not (1 <= limit <= 100) or offset < 0:
        return jsonify(error="limit must be 1..100 and offset >= 0"), 400

    result = notes
    if author is not None:
        result = [n for n in notes if n["author"] == author]

    result = sorted(result, key=lambda n: n[sort_field], reverse=(order == "desc"))

    return jsonify(result[offset : offset + limit])


@app.post("/notes")
def create_note():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="JSON object required"), 400

    if not is_valid_str(data.get("author")) or not is_valid_str(data.get("text")):
        return jsonify(error="fields 'author' and 'text' (non-empty strings) are required"), 400

    note = {
        "id": next(note_ids),
        "author": data["author"].strip(),
        "text": data["text"].strip(),
        "likes": 0
    }
    notes.append(note)
    save_notes()
    return jsonify(note), 201


@app.get("/notes/<int:note_id>")
def get_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    return jsonify(note)


@app.put("/notes/<int:note_id>")
def replace_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="JSON object required"), 400

    if not is_valid_str(data.get("author")) or not is_valid_str(data.get("text")):
        return jsonify(error="fields 'author' and 'text' (non-empty strings) are required"), 400

    note["author"] = data["author"].strip()
    note["text"] = data["text"].strip()
    save_notes()
    return jsonify(note), 200


@app.patch("/notes/<int:note_id>")
def edit_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="JSON object required"), 400

    if "author" not in data and "text" not in data:
        return jsonify(error="at least one of 'author' or 'text' is required"), 400

    if "author" in data and not is_valid_str(data["author"]):
        return jsonify(error="field 'author' must be a non-empty string"), 400

    if "text" in data and not is_valid_str(data["text"]):
        return jsonify(error="field 'text' must be a non-empty string"), 400

    if "author" in data:
        note["author"] = data["author"].strip()
    if "text" in data:
        note["text"] = data["text"].strip()

    save_notes()
    return jsonify(note), 200


@app.post("/notes/<int:note_id>/like")
def like_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)

    note["likes"] += 1
    save_notes()
    return jsonify(note), 200


@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    notes.remove(note)
    save_notes()
    return "", 204


@app.delete("/notes")
def delete_notes_by_author():
    author = request.args.get("author")
    if not is_valid_str(author):
        return jsonify(error="query parameter 'author' (non-empty) is required"), 400

    author = author.strip()
    old_count = len(notes)
    notes[:] = [n for n in notes if n["author"] != author]
    deleted_count = old_count - len(notes)

    if deleted_count > 0:
        save_notes()

    return jsonify(deleted=deleted_count), 200


@app.get("/authors")
def get_authors_stats():
    stats = {}
    for n in notes:
        author_name = n["author"]
        if author_name not in stats:
            stats[author_name] = {"author": author_name, "notes": 0, "likes": 0}
        stats[author_name]["notes"] += 1
        stats[author_name]["likes"] += n["likes"]

    result = sorted(stats.values(), key=lambda item: item["author"])
    return jsonify(result), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify(error="not found"), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(error="method not allowed"), 405


if __name__ == "__main__":
    app.run(debug=True)