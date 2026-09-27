from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import httpx
import sqlite3
import logging
from fastapi.middleware.cors import CORSMiddleware

# Configuração do Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="School Library API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn


with get_db_connection() as conn:
    conn.execute('''
                 CREATE TABLE IF NOT EXISTS books
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     isbn
                     TEXT,
                     title
                     TEXT,
                     author
                     TEXT,
                     status
                     TEXT
                 )
                 ''')


class CreateBook(BaseModel):
    isbn: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None


class UpdateBook(BaseModel):
    status: str


@app.post("/books/")
async def add_book(book: CreateBook):
    final_title = book.title or "Unknown Title"
    final_author = book.author or "Unknown Author"

    if book.isbn:
        logger.info(f"Processing ISBN: {book.isbn}")
        # Habilitando o redirecionamento automático
        async with httpx.AsyncClient(follow_redirects=True) as client:
            api_success = False

            # Attempt 1: BrasilAPI
            try:
                logger.info(f"Attempting primary API (BrasilAPI) for ISBN {book.isbn}...")
                url_primary = f"https://brasilapi.com.br/api/isbn/v1/{book.isbn}"
                response = await client.get(url_primary, timeout=5.0)

                if response.status_code == 200:
                    data = response.json()
                    final_title = data.get("title", final_title)
                    authors = data.get("authors", [])
                    if authors:
                        final_author = authors[0]
                    api_success = True
                    logger.info(f"Success! Data fetched from BrasilAPI for ISBN {book.isbn}")
                else:
                    logger.warning(f"BrasilAPI returned status code {response.status_code}")
            except Exception as e:
                logger.error(f"BrasilAPI request failed: {e}")

            # Attempt 2: Fallback to Open Library (Direct Route)
            if not api_success:
                try:
                    logger.info(f"Attempting fallback API (Open Library) for ISBN {book.isbn}...")
                    url_fallback = f"https://openlibrary.org/isbn/{book.isbn}.json"
                    response_fallback = await client.get(url_fallback, timeout=5.0)

                    if response_fallback.status_code == 200:
                        data_fallback = response_fallback.json()
                        final_title = data_fallback.get("title", final_title)
                        logger.info(f"Success! Data fetched from Open Library for ISBN {book.isbn}")
                    else:
                        logger.warning(f"Open Library returned status code {response_fallback.status_code}")
                except Exception as e:
                    logger.error(f"Open Library fallback request failed: {e}")
    else:
        logger.info("No ISBN provided. Skipping external API calls.")

    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO books (isbn, title, author, status) VALUES (?, ?, ?, ?)",
            (book.isbn, final_title, final_author, "Available")
        )
        conn.commit()
        logger.info(f"Book saved successfully to database with ID: {cursor.lastrowid}")
        return {"id": cursor.lastrowid, "isbn": book.isbn, "title": final_title, "author": final_author,
                "status": "Available"}


@app.get("/books/")
def list_books(
        skip: int = Query(0, description="Number of records to skip"),
        limit: int = Query(10, description="Limit of records returned"),
        status: Optional[str] = Query(None, description="Filter by book status")
):
    with get_db_connection() as conn:
        query = "SELECT * FROM books"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)

        query += " LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        books = conn.execute(query, params).fetchall()
        logger.info(f"Fetched {len(books)} books from database.")
        return [dict(b) for b in books]


@app.put("/books/{book_id}")
def update_status(book_id: int, book: UpdateBook):
    with get_db_connection() as conn:
        cursor = conn.execute("UPDATE books SET status = ? WHERE id = ?", (book.status, book_id))
        if cursor.rowcount == 0:
            logger.warning(f"Failed to update status. Book ID {book_id} not found.")
            raise HTTPException(status_code=404, detail="Book not found.")
        conn.commit()
        logger.info(f"Status of book ID {book_id} updated to {book.status}.")
        return {"message": "Status updated successfully"}


@app.delete("/books/{book_id}")
def remove_book(book_id: int):
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        if cursor.rowcount == 0:
            logger.warning(f"Failed to delete. Book ID {book_id} not found.")
            raise HTTPException(status_code=404, detail="Book not found.")
        conn.commit()
        logger.info(f"Book ID {book_id} deleted successfully.")
        return {"message": "Book removed successfully"}
