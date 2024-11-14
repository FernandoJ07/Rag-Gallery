from unittest.mock import patch

import pytest
from unittest import mock, TestCase
from fastapi import UploadFile, HTTPException, status
from app.core import ports
from app.usecases import RAGService, QueryRequest, UpdateRoleUserRequest, UserRequest
from app.core.models import User
from app.helpers.auth import get_password_hash, verify_password
from dotenv import load_dotenv

load_dotenv()


class TestRAGService(TestCase):
    def setUp(self) -> None:
        self.db_mock = mock.Mock(spec=ports.DatabasePort)
        self.document_repo_mock = mock.Mock(spec=ports.DocumentRepositoryPort)
        self.openai_adapter_mock = mock.Mock(spec=ports.LlmPort)
        self.rag_service = RAGService(
            self.db_mock, self.document_repo_mock, self.openai_adapter_mock
        )

    def test_save_document_should_save_document_when_valid_file(self) -> None:
        # Arrange
        file_mock = mock.Mock(spec=UploadFile)
        file_mock.filename = "test.pdf"
        file_mock.file = mock.Mock()
        file_mock.file.read.return_value = (
            b"Esta es una prueba para testear la subida y guardado de documentos"
        )

        # Act
        self.rag_service.save_document(file_mock)

        # Assert
        self.db_mock.save_document.assert_called_once()
        self.document_repo_mock.save_document.assert_called_once()

    def test_save_document_should_raise_valueerror_when_file_content_is_none(
        self,
    ) -> None:
        # Arrange
        file_mock = mock.Mock(spec=UploadFile)
        file_mock.filename = "invalid_file.pdf"
        file_mock.file = mock.Mock()
        file_mock.file.read.return_value = b""

        # Mockear el comportamiento de FileReader para devolver None
        with mock.patch("app.usecases.FileReader.read_file", return_value=None):
            # Act & Assert
            with self.assertRaises(ValueError) as context:
                self.rag_service.save_document(file_mock)
            self.assertEqual(
                str(context.exception),
                "Error reading content from the file: invalid_file.pdf",
            )

    def test_generate_answer_should_filter_out_documents_with_none_content(
        self,
    ) -> None:
        # Arrange
        query_data = QueryRequest(query="What is the capital of France?")
        documents = [
            mock.Mock(content="The capital of France is Paris."),
            mock.Mock(content=None),  # Este documento debería ser filtrado
        ]
        self.document_repo_mock.get_documents.return_value = documents
        self.openai_adapter_mock.generate_text.return_value = (
            "The capital of France is Paris."
        )

        # Act
        result = self.rag_service.generate_answer(query_data)

        # Assert
        self.document_repo_mock.get_documents.assert_called_once_with(
            "What is the capital of France?", self.openai_adapter_mock
        )
        self.openai_adapter_mock.generate_text.assert_called_once_with(
            prompt="What is the capital of France?",
            retrieval_context="The capital of France is Paris.",
        )
        assert result == "The capital of France is Paris."

    def test_sign_up_should_save_user_with_hashed_password(self) -> None:
        # Arrange
        user_request = UserRequest(
            username="john", password="password123", is_admin=False
        )

        # Act
        self.rag_service.sign_up(user_request)

        # Assert
        self.db_mock.save_user.assert_called_once()
        saved_user = self.db_mock.save_user.call_args[0][0]
        assert saved_user.username == "john"
        assert not saved_user.is_admin
        assert verify_password("password123", saved_user.password)

    def test_authenticate_user_should_return_access_token_when_password_is_correct(
        self,
    ) -> None:
        # Arrange
        hashed_password = get_password_hash("password123")
        user = User(
            uid="123", username="john", password=hashed_password, is_admin=False
        )
        self.db_mock.get_user.return_value = user
        expected_token = "mocked_jwt_token"

        with patch(
            "app.usecases.create_access_token_for_user", return_value=expected_token
        ):
            # Act
            result = self.rag_service.authenticate_user("john", "password123")

            # Assert
            self.db_mock.get_user.assert_called_once_with("john")
            assert result == expected_token

    def test_authenticate_user_should_raise_http_exception_when_password_is_incorrect(
        self,
    ) -> None:
        # Arrange
        hashed_password = get_password_hash("password123")
        user = User(
            uid="123", username="john", password=hashed_password, is_admin=False
        )
        self.db_mock.get_user.return_value = user

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            self.rag_service.authenticate_user("john", "wrongpassword")

        self.db_mock.get_user.assert_called_once_with("john")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Error en la autenticación después del registro"

    def test_get_user_should_return_user_when_user_exists(self) -> None:
        # Arrange
        user = User(
            uid="6b078b11-6ab2-468f-9023-b741a9320c54",
            username="pedro",
            password="pedro123",
            is_admin=False,
        )
        self.db_mock.get_user.return_value = user

        # Act
        result = self.rag_service.get_user("pedro")

        # Assert
        self.db_mock.get_user.assert_called_once_with("pedro")
        assert result == user

    def test_update_role_should_update_user_role_when_called(self) -> None:
        # Arrange
        update_role_data = UpdateRoleUserRequest(
            uid="5cf9a503-363c-4a41-96d2-b11e473d9728", is_admin=True
        )

        # Act
        self.rag_service.update_role(update_role_data)

        # Assert
        self.db_mock.update_user_role.assert_called_once_with(
            "5cf9a503-363c-4a41-96d2-b11e473d9728", True
        )

    def test_get_users_should_return_all_users(self) -> None:
        # Arrange
        users = [
            User(
                uid="b7265985-38ed-4a22-8ff7-931d47c8a33e",
                username="user1",
                password="user123",
                is_admin=True,
            ),
            User(
                uid="886aaa60-9629-4315-821a-e5b04398389c",
                username="user2",
                password="user",
                is_admin=False,
            ),
        ]
        self.db_mock.get_users.return_value = users

        # Act
        result = self.rag_service.get_users()

        # Assert
        self.db_mock.get_users.assert_called_once()
        assert result == users
