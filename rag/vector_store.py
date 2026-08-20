import chromadb
from pathlib import Path

from rag.embeddings import create_embeddings


CHROMA_PATH = Path("data/chroma")


def get_client():
    CHROMA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    return chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )


def get_collection():
    client = get_client()

    return client.get_or_create_collection(
        name="financial_documents"
    )


def clear_collection():
    client = get_client()

    try:
        client.delete_collection(
            name="financial_documents"
        )
    except Exception:
        pass


def add_documents(pages):
    collection = get_collection()

    documents = []
    ids = []
    metadatas = []

    for index, page in enumerate(pages):
        text = page["text"].strip()

        if not text:
            continue

        documents.append(text)

        ids.append(
            f"page_{page['page']}_{index}"
        )

        metadatas.append({
            "page": page["page"]
        })

    if not documents:
        return

    embeddings = create_embeddings(documents)

    collection.add(
        documents=documents,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )


def search_documents(query, top_k=5):
    collection = get_collection()

    query_embedding = create_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get("documents", [[]])[0]

    metadatas = results.get("metadatas", [[]])[0]

    output = []

    for document, metadata in zip(
        documents,
        metadatas
    ):
        output.append({
            "text": document,
            "page": metadata.get("page")
        })

    return output