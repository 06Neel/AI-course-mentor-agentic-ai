from config.settings import Settings


class EmbeddingEngine:
    """Legacy embedding engine - kept for backward compatibility.

    ChromaDB handles embeddings internally via its default embedding function.
    This class is not used by the current RAG pipeline.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or Settings.EMBEDDING_MODEL
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_documents(self, texts: list[str]):
        return self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

    def embed_query(self, text: str):
        return self.model.encode([text], show_progress_bar=False, convert_to_numpy=True)

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()
