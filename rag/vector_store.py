import json
import math
import sqlite3
from pathlib import Path

from rag.embeddings import create_embeddings


DATABASE_PATH = Path("data/rag.db")


def get_connection():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_vector_database():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page INTEGER,
            text TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def clear_collection():

    initialize_vector_database()

    connection = get_connection()

    connection.execute(
        "DELETE FROM documents"
    )

    connection.commit()
    connection.close()


def add_documents(pages):

    initialize_vector_database()

    documents = []

    for page in pages:

        text = page.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        text = text[:6000]

        documents.append({
            "page": page.get(
                "page",
                page.get(
                    "page_number",
                    0
                )
            ),
            "text": text
        })

    if not documents:
        raise ValueError(
            "No readable text was extracted from the PDF."
        )

    texts = [
        document["text"]
        for document in documents
    ]

    embeddings = create_embeddings(
        texts
    )

    if not embeddings:
        raise ValueError(
            "No embeddings were generated."
        )

    if len(documents) != len(embeddings):
        raise ValueError(
            "Number of documents and embeddings "
            "does not match."
        )

    connection = get_connection()

    try:

        for document, embedding in zip(
            documents,
            embeddings
        ):

            connection.execute(
                """
                INSERT INTO documents
                (page, text, embedding)
                VALUES (?, ?, ?)
                """,
                (
                    document["page"],
                    document["text"],
                    json.dumps(
                        embedding
                    )
                )
            )

        connection.commit()

    finally:

        connection.close()


def cosine_similarity(
    vector_a,
    vector_b
):

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b
        )
    )

    magnitude_a = math.sqrt(
        sum(
            a * a
            for a in vector_a
        )
    )

    magnitude_b = math.sqrt(
        sum(
            b * b
            for b in vector_b
        )
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return (
        dot_product /
        (magnitude_a * magnitude_b)
    )


def search_documents(
    query,
    top_k=3
):

    initialize_vector_database()

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT page, text, embedding
        FROM documents
        """
    ).fetchall()

    connection.close()

    if not rows:
        return []

    query_embedding = create_embeddings(
        [query]
    )[0]

    results = []

    for row in rows:

        stored_embedding = json.loads(
            row["embedding"]
        )

        score = cosine_similarity(
            query_embedding,
            stored_embedding
        )

        results.append({
            "page": row["page"],
            "text": row["text"],
            "score": score
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]


initialize_vector_database()