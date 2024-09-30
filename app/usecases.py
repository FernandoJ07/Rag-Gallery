import os
from fastapi import UploadFile
from app.core.models import Document
from app.core import ports
from app.helpers.strategies_poc import FileReader


class RAGService:
    def __init__(self, db: ports.DatabasePort, document_repo: ports.DocumentRepositoryPort, openai_adapter: ports.LlmPort) -> None:
        self.db = db
        self.document_repo = document_repo
        self.openai_adapter = openai_adapter

    def generate_answer(self, query: str) -> str:
        documents = self.document_repo.get_documents(query)
        print(f"Documents: {documents}")
        context = " ".join([doc.content for doc in documents])
        return self.openai_adapter.generate_text(prompt=query, retrieval_context=context)

    def save_document(self, file: UploadFile) -> None:
        # Obtener el nombre del archivo
        file_name = file.filename

        # Crear la carpeta 'media' si no existe
        os.makedirs('media', exist_ok=True)

        # Guardar el archivo en la carpeta 'media'
        file_path = os.path.join('media', file_name)
        with open(file_path, 'wb') as f:
            f.write(file.file.read())

        # Crear modelo ducumento con valores iniciales
        document = Document(nombre=file_name, ruta=file_path)
        # Guardar información del documento en MongoDB
        self.db.save_document(document)

        # Obtengo el contenido del documento
        content = FileReader(document.ruta).read_file()
        # Realiza embedding, chunks y guarda en ChromaDB
        self.document_repo.save_document(document, content, self.openai_adapter)

    def sing_up(self, username: str, password: str) -> None:
        self.db.save_user(username, password)