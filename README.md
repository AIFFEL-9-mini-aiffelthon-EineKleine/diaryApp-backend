# Diary Application (back-end)

> This is the backend of a diary application that provides APIs for managing diary entries, keywords (emotions), and tags. Built with FastAPI and SQLite, it supports data synchronization with the frontend application. The backend handles data storage, retrieval, and updates, ensuring consistency across clients in server mode.

## 1. Quick Start

### 1.1 Prerequisites

- **Python**: Version 3.6 or higher
- **pip**: Python package installer

### 1.2 Steps

1. **Clone the Repository**

   ```bash
    git clone https://github.com/AIFFEL-9-mini-aiffelthon-EineKleine/diaryApp-backend
    cd diaryApp-backend
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Database Initialization**
   - The `sql_server.py` script will initialize the SQLite database (`diary_server.db`) automatically when the server starts.

5. **Run the FastAPI Server**
    ```bash
    fastapi dev sql_server.py
    ```
	  If you prefer using `uvicorn` command directly, use the script following.
    ```bash
    uvicorn sql_server:app --reload --host 0.0.0.0 --port 8000
    ```
  - The server will be accessible at `http://localhost:8000`.

## 2. Features

- **CRUD Operations**: Create, read, update, and delete diary entries.
- **Keyword Management**: Update keywords associated with diary entries.
- **Tagging API**: Add and manage tags for specific sentences within entries.
- **Synchronization**: Supports data synchronization with the frontend application.
- **RESTful API**: Provides a RESTful interface for all operations.

## 3. Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs with Python.
	- **Uvicorn**: Lightning-fast ASGI server for Python.
- **SQLite3**: Lightweight disk-based database.
- **Pydantic**: Data parsing and validation using Python type annotations.

## 4. Configuration

### 4.1 CORS Settings

In `sql_server.py`, ensure the `origins` list includes the origin of your frontend application (e.g., `http://localhost:3000`).

```python
origins = [
    "http://localhost:3000",
    # Add other origins if necessary
]
```

## 5. Usage (API Endpoints)

### 5.1 Diary Entries

- **Create Entry**
	- **Endpoint**: `POST /api/diary`
	- **Description**: Create a new diary entry.
	- **Payload**:

    ```json
    {
      "content": "Entry content",
      "created_at": "Optional timestamp",
      "keywords": ["keyword1", "keyword2"]
    }
    ```

- **Get All Entries**
	- **Endpoint**: `GET /api/diary`
	- **Description**: Retrieve all diary entries.

- **Get Single Entry**
	- **Endpoint**: `GET /api/diary/{entry_id}`
	- **Description**: Retrieve a specific diary entry.

- **Update Entry Keywords**
	- **Endpoint**: `PUT /api/diary/{entry_id}/keywords`
	- **Description**: Update keywords for a diary entry.
	- **Payload**:

    ```json
    {
      "keywords": ["updated_keyword1", "updated_keyword2"]
    }
    ```

### 5.2 Keywords (emotions)

- **Get All Keywords**
	- **Endpoint**: `GET /api/keywords`
	- **Description**: Retrieve all keywords(emotions) associated with entries.

### 5.3 Tags

- **Add Tag**
	- **Endpoint**: `POST /api/tags`
	- **Description**: Add a tag to a specific sentence in an entry.
	- **Payload**:

    ```json
    {
      "entry_id": 1,
      "sentence_index": 0,
      "tag": "tag_text"
    }
    ```

- **Get All Tags**
	- **Endpoint**: `GET /api/tags`
	- **Description**: Retrieve all tags.

- **Delete Tag**
	- **Endpoint**: `DELETE /api/tags/{tag_id}`
	- **Description**: Delete a specific tag.

## 6. Project Structure

```
diary-app-backend/
├── sql_server.py
├── diary_server.db
├── requirements.txt
└── README.md
```

---

### License

This project is licensed under the MIT License.

### Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework.
- [Uvicorn](https://www.uvicorn.org/) for the ASGI server. Default for FastAPI.