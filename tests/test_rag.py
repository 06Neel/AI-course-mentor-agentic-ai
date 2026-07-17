import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.loader import DocumentLoader, DocumentChunk


class TestDocumentLoader:
    def setup_method(self):
        self.loader = DocumentLoader(chunk_size=100, chunk_overlap=20)

    def test_chunk_creation(self):
        text = " ".join([f"word{i}" for i in range(200)])
        chunks = self.loader._create_chunks([(text, "test.pdf", 1)])
        assert len(chunks) > 0
        assert all(isinstance(c, DocumentChunk) for c in chunks)

    def test_chunk_metadata(self):
        text = "This is a test document with some content."
        chunks = self.loader._create_chunks([(text, "test.pdf", 5)])
        assert chunks[0].source == "test.pdf"
        assert chunks[0].page == 5
        assert chunks[0].chunk_id == 0

    def test_empty_text(self):
        chunks = self.loader._create_chunks([("", "test.pdf", 1)])
        assert len(chunks) == 0

    def test_multiple_pages(self):
        pages = [
            ("Page one content", "doc.pdf", 1),
            ("Page two content", "doc.pdf", 2),
        ]
        chunks = self.loader._create_chunks(pages)
        assert len(chunks) == 2
        assert chunks[0].page == 1
        assert chunks[1].page == 2


if __name__ == "__main__":
    test = TestDocumentLoader()
    test.setup_method()
    test.test_chunk_creation()
    test.test_chunk_metadata()
    test.test_empty_text()
    test.test_multiple_pages()
    print("All loader tests passed!")
