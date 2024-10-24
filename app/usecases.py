from datetime import timedelta
from typing import Optional

from exceptiongroup import catch
from fastapi import UploadFile
from pydantic import BaseModel
from app.core.models import Document, User
from app.core import ports
from app.helpers.auth import get_password_hash, verify_password, create_access_token
from app.helpers.strategies_poc import FileReader
from app import configurations

configs = configurations.Configs()


class QueryRequest(BaseModel):
    query: str

class UserRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False

class UpdateRoleUserRequest(BaseModel):
    uid: str
    is_admin: bool


def create_access_token_for_user(user: User):
    access_token_expires = timedelta(minutes=configs.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.uid}, expires_delta=access_token_expires
    )
    return access_token


class RAGService:
    def __init__(self, db: ports.DatabasePort, document_repo: ports.DocumentRepositoryPort, openai_adapter: ports.LlmPort) -> None:
        self.db = db
        self.document_repo = document_repo
        self.openai_adapter = openai_adapter

    def save_document(self, file: UploadFile) -> None:

        #Procesar la informacion del archivo
        file_name = file.filename
        #Contenido del archivo en bytes
        file_content = file.file.read()
        document = Document(nombre=file_name)
        extension = file_name.split('.')[-1]
        content = FileReader(file_content, extension).read_file()

        # Guardar información del documento en MongoDB
        self.db.save_document(document)

        # Realizar embedding, chunks y guardar en ChromaDB
        self.document_repo.save_document(document, content, self.openai_adapter)
    def generate_answer(self, query_data: QueryRequest) -> str:
        query = query_data.query
        documents = self.document_repo.get_documents(query, self.openai_adapter)
        print(f"Documents: {documents}")
        context = " ".join([doc.content for doc in documents])
        return self.openai_adapter.generate_text(prompt=query, retrieval_context=context)
    def get_document(self, document_id: str) -> Document:
        return self.db.get_document(document_id)
    def get_vectors(self):
        return self.document_repo.get_vectors()

    def sign_up(self, user_request: UserRequest) -> None:
        hashed_password = get_password_hash(user_request.password)
        user = User(username=user_request.username,
                    password=hashed_password,
                    is_admin=user_request.is_admin)
        self.db.save_user(user)
    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self.db.get_user(username)
        if not user or not verify_password(password, user.password):
            return None
        return user
    def get_user(self, username: str) -> User:
        return self.db.get_user(username)
    def update_role(self, user: UpdateRoleUserRequest) -> None:
        self.db.update_user_role(user.uid, user.is_admin)
    def get_users(self):
        return self.db.get_users()