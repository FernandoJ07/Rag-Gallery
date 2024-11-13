from abc import ABC, abstractmethod
from typing import List, Optional
from app.core import models
from app.core.models import User


class DocumentRepositoryPort(ABC):
    @abstractmethod
    def save_document(
        self, document: models.Document, content: str | None, openai_client: object
    ) -> None:
        pass

    @abstractmethod
    def get_documents(
        self, query: str, openai_client: object, n_results: Optional[int] = None
    ) -> List[models.Document]:
        pass

    @abstractmethod
    def get_vectors(self) -> object:
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
    def get_user(self, username: str) -> models.User:
        pass

    @abstractmethod
    def update_user_role(self, uid: str, is_admin: bool) -> None:
        pass

    @abstractmethod
    def save_document(self, document: models.Document) -> None:
        pass

    @abstractmethod
    def get_document(self, document_id: str) -> Optional[models.Document]:
        pass

    @abstractmethod
    def get_users(self) -> List[models.User]:
        pass
