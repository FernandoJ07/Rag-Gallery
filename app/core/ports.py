from abc import ABC, abstractmethod
from typing import List
from app.core import models
from app.core.models import User


class DocumentRepositoryPort(ABC):
    @abstractmethod
    def save_document(self, document: models.Document, content: str, openai_client) -> None:
        pass

    @abstractmethod
    def get_documents(self, query: str, openai_client ,n_results: int | None = None) -> List[models.Document]:
        pass

    @abstractmethod
    def get_vectors(self):
        pass

class LlmPort(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, retrieval_context: str) -> str:
        pass

class DatabasePort(ABC):
    @abstractmethod
    def save_user(self, user: User) -> None:
        pass

    @abstractmethod
    def get_user(self, uid: str) -> models.User:
        pass

    @abstractmethod
    def update_user_role(self, uid: str, is_admin: bool) -> str:
        pass

    @abstractmethod
    def save_document(self, document: models.Document) -> None:
        pass

    @abstractmethod
    def get_document(self, document_id: str) -> models.Document | None:
        pass
