import os
from pathlib import Path

from config.settings import Settings
from rag.loader import DocumentLoader, DocumentChunk
from rag.vector_store import VectorStore


class DocumentProcessor:
    def __init__(self):
        self.settings = Settings()
        self.loader = DocumentLoader(
            chunk_size=self.settings.CHUNK_SIZE,
            chunk_overlap=self.settings.CHUNK_OVERLAP,
        )
        self.vector_store = VectorStore()

    def validate_file(self, file) -> tuple[bool, str]:
        if file is None:
            return False, "No file provided"

        filename = file.name
        ext = Path(filename).suffix.lower().lstrip(".")

        if ext not in self.settings.SUPPORTED_FILE_TYPES:
            return False, f"Unsupported file type: .{ext}. Supported: {', '.join(self.settings.SUPPORTED_FILE_TYPES)}"

        file.seek(0, os.SEEK_END)
        size_mb = file.tell() / (1024 * 1024)
        file.seek(0)

        if size_mb > self.settings.MAX_UPLOAD_SIZE_MB:
            return False, f"File too large: {size_mb:.1f}MB. Max: {self.settings.MAX_UPLOAD_SIZE_MB}MB"

        return True, "Valid"

    def validate_batch(self, files: list) -> tuple[bool, str]:
        if len(files) > self.settings.MAX_FILES_PER_UPLOAD:
            return False, f"Too many files: {len(files)}. Max: {self.settings.MAX_FILES_PER_UPLOAD} per upload"
        return True, "Valid"

    def process_uploaded_file(self, file) -> tuple[bool, str, int]:
        valid, msg = self.validate_file(file)
        if not valid:
            return False, msg, 0

        save_path = self.settings.DATA_DIR / file.name
        file.seek(0)
        with open(save_path, "wb") as f:
            f.write(file.read())

        try:
            chunks = self.loader.load_file(str(save_path))
            if not chunks:
                return False, "No text content extracted from file", 0

            if self.vector_store.is_loaded:
                self.vector_store.add_chunks(chunks)
            else:
                self.vector_store.create_index(chunks)

            return True, f"Successfully processed {file.name}", len(chunks)
        except Exception as e:
            return False, f"Error processing file: {str(e)}", 0

    def get_uploaded_files(self) -> list[str]:
        if not self.settings.DATA_DIR.exists():
            return []
        return [
            f.name
            for f in self.settings.DATA_DIR.iterdir()
            if f.suffix.lower() in [".pdf", ".docx", ".pptx"]
        ]

    def get_stats(self) -> dict:
        files = self.get_uploaded_files()
        return {
            "total_files": len(files),
            "files": files,
            "total_chunks": self.vector_store.total_chunks,
            "index_ready": self.vector_store.is_loaded,
        }
