from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            keyword TEXT NOT NULL,
            FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()

init_db()

# Define the data models
class DiaryEntry(BaseModel):
    content: str
    created_at: Optional[str] = None
    keywords: Optional[List[str]] = []

class Tag(BaseModel):
    entry_id: int
    sentence_index: int
    tag: str

class Keyword(BaseModel):
    entry_id: int
    keyword: str

# New Pydantic model for updating keywords
class KeywordsUpdate(BaseModel):
    keywords: List[str]

# CRUD Endpoints for Diary Entries
@app.post("/api/diary")
async def create_diary_entry(entry: DiaryEntry):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        if entry.created_at:
            cursor.execute("INSERT INTO entries (content, created_at) VALUES (?, ?)", (entry.content, entry.created_at))
        else:
            cursor.execute("INSERT INTO entries (content) VALUES (?)", (entry.content,))
        entry_id = cursor.lastrowid

        # Insert keywords if any
        for kw in entry.keywords:
            cursor.execute(
                "INSERT INTO keywords (entry_id, keyword) VALUES (?, ?)",
                (entry_id, kw.strip())
            )

        conn.commit()
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
        entries = []
        for row in rows:
            entry = {"id": row[0], "content": row[1], "created_at": row[2]}
            # Fetch keywords for the entry
            cursor.execute("SELECT keyword FROM keywords WHERE entry_id = ?", (row[0],))
            keywords = [kw[0] for kw in cursor.fetchall()]
            entry["keywords"] = keywords
            entries.append(entry)
        conn.close()
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/diary/{entry_id}")
async def get_diary_entry(entry_id: int):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Entry not found.")
        entry = {"id": row[0], "content": row[1], "created_at": row[2]}
        # Fetch keywords for the entry
        cursor.execute("SELECT keyword FROM keywords WHERE entry_id = ?", (entry_id,))
        keywords = [kw[0] for kw in cursor.fetchall()]
        entry["keywords"] = keywords
        conn.close()
        return entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/diary/{entry_id}/keywords")
async def update_entry_keywords(entry_id: int, keywords_update: KeywordsUpdate):
    try:
        keywords = keywords_update.keywords
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        # Check if the entry exists
        cursor.execute("SELECT id FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Entry not found.")

        # Delete existing keywords for the entry
        cursor.execute("DELETE FROM keywords WHERE entry_id = ?", (entry_id,))

        # Insert new keywords
        for kw in keywords:
            cursor.execute(
                "INSERT INTO keywords (entry_id, keyword) VALUES (?, ?)",
                (entry_id, kw.strip())
            )

        conn.commit()
        conn.close()
        return {"message": "Keywords updated successfully."}
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

@app.get("/api/tags")
async def get_all_tags():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, entry_id, sentence_index, tag FROM tags")
        rows = cursor.fetchall()
        tags = [{"id": row[0], "entry_id": row[1], "sentence_index": row[2], "tag": row[3]} for row in rows]
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

# CRUD Endpoints for Keywords
@app.get("/api/keywords")
async def get_all_keywords():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, entry_id, keyword FROM keywords")
        rows = cursor.fetchall()
        keywords = [{"id": row[0], "entry_id": row[1], "keyword": row[2]} for row in rows]
        conn.close()
        return keywords
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))