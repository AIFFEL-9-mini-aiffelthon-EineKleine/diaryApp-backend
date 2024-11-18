from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",  # React app origin
    # Add other origins if necessary
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE = "diary_server.db"

# Initialize the database and create tables if not exist
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            sentence_index INTEGER NOT NULL,
            tag TEXT NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()

init_db()

# Define the data models
class DiaryEntry(BaseModel):
    content: str

class Tag(BaseModel):
    entry_id: int
    sentence_index: int
    tag: str

# CRUD Endpoints for Diary Entries
@app.post("/api/diary")
async def create_diary_entry(entry: DiaryEntry):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO entries (content) VALUES (?)", (entry.content,))
        conn.commit()
        entry_id = cursor.lastrowid
        conn.close()
        return {"message": "Diary entry created.", "entry_id": entry_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/diary")
async def get_diary_entries():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries ORDER BY created_at DESC")
        rows = cursor.fetchall()
        entries = [{"id": row[0], "content": row[1], "created_at": row[2]} for row in rows]
        conn.close()
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/diary/{entry_id}")
async def update_diary_entry(entry_id: int, entry: DiaryEntry):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("UPDATE entries SET content = ? WHERE id = ?", (entry.content, entry_id))
        conn.commit()
        conn.close()
        return {"message": "Diary entry updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/diary/{entry_id}")
async def delete_diary_entry(entry_id: int):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()
        return {"message": "Diary entry deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# CRUD Endpoints for Tags
@app.post("/api/tags")
async def create_tag(tag: Tag):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tags (entry_id, sentence_index, tag) VALUES (?, ?, ?)",
            (tag.entry_id, tag.sentence_index, tag.tag)
        )
        conn.commit()
        tag_id = cursor.lastrowid
        conn.close()
        return {"message": "Tag created.", "tag_id": tag_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tags/{entry_id}")
async def get_tags_for_entry(entry_id: int):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, sentence_index, tag FROM tags WHERE entry_id = ?", (entry_id,))
        rows = cursor.fetchall()
        tags = [{"id": row[0], "sentence_index": row[1], "tag": row[2]} for row in rows]
        conn.close()
        return tags
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/tags/{tag_id}")
async def delete_tag(tag_id: int):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Tag not found.")
        conn.commit()
        conn.close()
        return {"message": "Tag deleted."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))