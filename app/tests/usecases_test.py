from unittest import mock, TestCase
from fastapi import UploadFile
from app.core import ports
from app.usecases import RAGService, QueryRequest, UpdateRoleUserRequest
from app.core.models import User
# from fastapi.testclient import TestClient
# from io import BytesIO
# from app.main import app
from dotenv import load_dotenv

load_dotenv()

class TestRAGService(TestCase):
    def setUp(self):
        self.db_mock = mock.Mock(spec=ports.DatabasePort)
        self.document_repo_mock = mock.Mock(spec=ports.DocumentRepositoryPort)
        self.openai_adapter_mock = mock.Mock(spec=ports.LlmPort)
        self.rag_service = RAGService(self.db_mock, self.document_repo_mock, self.openai_adapter_mock)

    def test_save_document_should_save_document_when_valid_file(self):
        # Arrange
        file_mock = mock.Mock(spec=UploadFile)
        file_mock.filename = "test.pdf"
        file_mock.file = mock.Mock()
        file_mock.file.read.return_value = b"Esta es una prueba para testear la subida y guardado de documentos"

        # Act
        self.rag_service.save_document(file_mock)

        # Assert
        self.db_mock.save_document.assert_called_once()
        self.document_repo_mock.save_document.assert_called_once()

    def test_generate_answer_should_return_text_when_query_valid(self):
        # Arrange
        query_data = QueryRequest(query="Que significa el color amarillo en la bandera de colombia?")
        documents = [mock.Mock(content="Siginfica las riquezas de la nación.")]
        self.document_repo_mock.get_documents.return_value = documents
        self.openai_adapter_mock.generate_text.return_value = "Siginfica las riquezas de la nación."

        # Act
        result = self.rag_service.generate_answer(query_data)

        # Assert
        self.document_repo_mock.get_documents.assert_called_once_with("Que significa el color amarillo en la bandera de colombia?", self.openai_adapter_mock)
        self.openai_adapter_mock.generate_text.assert_called_once()
        assert result == "Siginfica las riquezas de la nación."

    def test_get_user_should_return_user_when_user_exists(self):
        # Arrange
        user = User(uid="6b078b11-6ab2-468f-9023-b741a9320c54", username="pedro", password="pedro123", is_admin=False)
        self.db_mock.get_user.return_value = user

        # Act
        result = self.rag_service.get_user("pedro")

        # Assert
        self.db_mock.get_user.assert_called_once_with("pedro")
        assert result == user

    def test_update_role_should_update_user_role_when_called(self):
        # Arrange
        update_role_data = UpdateRoleUserRequest(uid="5cf9a503-363c-4a41-96d2-b11e473d9728", is_admin=True)

        # Act
        self.rag_service.update_role(update_role_data)

        # Assert
        self.db_mock.update_user_role.assert_called_once_with("5cf9a503-363c-4a41-96d2-b11e473d9728", True)

    def test_get_users_should_return_all_users(self):
        # Arrange
        users = [User(uid="b7265985-38ed-4a22-8ff7-931d47c8a33e", username="user1", password="user123", is_admin=True),
                 User(uid="886aaa60-9629-4315-821a-e5b04398389c", username="user2", password="user", is_admin=False)]
        self.db_mock.get_users.return_value = users

        # Act
        result = self.rag_service.get_users()

        # Assert
        self.db_mock.get_users.assert_called_once()
        assert result == users


    # def test_should_generate_answer_when_document_is_uploaded_and_query_is_made(self):
    #     # Arrange
    #     client = TestClient(app)
    #     file_data = {
    #         "file": ("test_file.txt", BytesIO(b"Contenido de prueba de un archivo random"), "text/plain")
    #     }
    #     # Act
    #     response_save_document = client.post("/save-document/", files=file_data)
    #     #Assert
    #     assert response_save_document.status_code == 201
    #     assert response_save_document.json() == {"status": "Document saved successfully"}
    #
    #     # Arrange
    #     query_data = {
    #         "query": "¿Qué contiene el archivo?"
    #     }
    #     # Act
    #     response_generate_answer = client.post("/generate-answer/", json=query_data)
    #     # Assert
    #     assert response_generate_answer.status_code == 201
    #     assert "respuesta" in response_generate_answer.json()



