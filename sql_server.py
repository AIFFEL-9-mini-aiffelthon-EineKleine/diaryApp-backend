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
    conn.commit()
    conn.close()

init_db()

# Define the data model
class DiaryEntry(BaseModel):
    content: str

# CRUD Endpoints
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
    