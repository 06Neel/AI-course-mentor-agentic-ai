import uuid
import chromadb
from chromadb.config import Settings as ChromaSettings

from config.settings import Settings
from rag.loader import DocumentChunk


class VectorStore:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if VectorStore._initialized:
            return
        VectorStore._initialized = True
        self.settings = Settings()
        self._client = None
        self._collection = None

    @property
    def client(self):
        if self._client is None:
            db_path = str(self.settings.VECTOR_DB_DIR / "chroma_db")
            self._client = chromadb.PersistentClient(
                path=db_path,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name="course_documents",
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def create_index(self, chunks: list[DocumentChunk]):
        self.client.delete_collection("course_documents")
        self._collection = None
        self.add_chunks(chunks)

    def add_chunks(self, new_chunks: list[DocumentChunk]):
        if not new_chunks:
            return

        ids = [f"{c.source}_{c.page}_{uuid.uuid4().hex[:8]}" for c in new_chunks]
        documents = [c.text for c in new_chunks]
        metadatas = [{"source": c.source, "page": c.page, "chunk_id": c.chunk_id} for c in new_chunks]

        batch_size = 100
        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i : i + batch_size],
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )

    def search(self, query: str, top_k: int = None) -> list[tuple[DocumentChunk, float]]:
        top_k = top_k or Settings.TOP_K_RESULTS
        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count()),
        )

        output = []
        if results and results["documents"]:
            for doc, meta, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                chunk = DocumentChunk(
                    text=doc,
                    source=meta.get("source", "unknown"),
                    page=meta.get("page", 0),
                    chunk_id=meta.get("chunk_id", 0),
                    metadata=meta,
                )
                output.append((chunk, distance))
        return output

    def reset(self):
        self.client.delete_collection("course_documents")
        self._collection = None

    @property
    def total_chunks(self) -> int:
        return self.collection.count()

    @property
    def is_loaded(self) -> bool:
        return self.collection.count() > 0

    @property
    def file_count(self) -> int:
        if self.collection.count() == 0:
            return 0
        all_meta = self.collection.get(include=["metadatas"])["metadatas"]
        return len(set(m.get("source", "") for m in all_meta))
