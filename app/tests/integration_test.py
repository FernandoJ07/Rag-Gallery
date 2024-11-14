from unittest.mock import Mock, patch
import pytest
from pymongo import MongoClient
from app.adapters.database_adapter import MongoDbAdapter
from app.adapters.openai_adapter import OpenAIAdapter
from app.core import ports
from app.core.models import User, Document
from app.usecases import RAGService


@pytest.fixture
def mock_document_repo() -> Mock:
    return Mock(spec=ports.DocumentRepositoryPort)


@pytest.fixture
def mock_openai_adapter() -> Mock:
    return Mock(spec=ports.LlmPort)


@pytest.fixture(scope="function")
def mongo_db() -> MongoClient:
    client = MongoClient("mongodb://127.0.0.1:27017")
    db = client["test_rag_db"]
    db.users.delete_many({})
    db.documents.delete_many({})
    yield db
    client.drop_database("test_rag_db")


@pytest.fixture
def mongo_adapter(mongo_db: MongoClient) -> MongoDbAdapter:
    return MongoDbAdapter("mongodb://127.0.0.1:27017", db_name="test_rag_db")


@pytest.fixture
def rag_service(
    mongo_adapter: MongoDbAdapter, mock_document_repo: Mock, mock_openai_adapter: Mock
) -> RAGService:
    return RAGService(
        db=mongo_adapter,
        document_repo=mock_document_repo,
        openai_adapter=mock_openai_adapter,
    )


# Mongo Adapter Tests
def test_should_save_user_and_get_user_when_user_is_saved(
    mongo_adapter: MongoDbAdapter, mongo_db: MongoClient
) -> None:
    # Arrange
    user = User(uid="1", username="test_user", password="secret", is_admin=False)

    # Act
    mongo_adapter.save_user(user)
    retrieved_user = mongo_adapter.get_user("test_user")

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.username == "test_user"
    assert retrieved_user.password == "secret"
    assert not retrieved_user.is_admin


def test_should_raise_error_when_user_not_found(mongo_adapter: MongoDbAdapter) -> None:
    # Act and Assert
    with pytest.raises(
        ValueError, match="Usuario con nombre 'nonexistent_user' no encontrado."
    ):
        mongo_adapter.get_user("nonexistent_user")


def test_should_update_user_role_when_user_role_is_updated(
    mongo_adapter: MongoDbAdapter, mongo_db: MongoClient
) -> None:
    # Arrange
    user = User(uid="1", username="admin_user", password="secret", is_admin=False)
    mongo_adapter.save_user(user)

    # Act
    mongo_adapter.update_user_role("1", True)
    updated_user = mongo_adapter.get_user("admin_user")

    # Assert
    assert updated_user.is_admin is True


def test_should_save_document_and_get_document_when_document_is_saved(
    mongo_adapter: MongoDbAdapter, mongo_db: MongoClient
) -> None:
    # Arrange
    document = Document(document_id="doc_1", nombre="Test Document")

    # Act
    mongo_adapter.save_document(document)
    retrieved_document = mongo_adapter.get_document("doc_1")

    # Assert
    assert retrieved_document is not None
    assert retrieved_document.document_id == "doc_1"
    assert retrieved_document.nombre == "Test Document"


def test_should_return_none_when_document_not_found(
    mongo_adapter: MongoDbAdapter,
) -> None:
    # Act
    document = mongo_adapter.get_document("nonexistent_doc")

    # Assert
    assert document is None


def test_should_return_all_users_when_users_exist(
    mongo_adapter: MongoDbAdapter, mongo_db: MongoClient
) -> None:
    # Arrange
    user1 = User(uid="1", username="user1", password="pass1", is_admin=False)
    user2 = User(uid="2", username="user2", password="pass2", is_admin=True)
    mongo_adapter.save_user(user1)
    mongo_adapter.save_user(user2)

    # Act
    users = mongo_adapter.get_users()

    # Assert
    assert len(users) == 2
    assert users[0].username == "user1"
    assert users[1].username == "user2"


# OpenAI Adapter Tests


@pytest.fixture
def mock_openai_client() -> Mock:
    return Mock()


@pytest.fixture
def openai_adapter(mock_openai_client: Mock) -> OpenAIAdapter:
    with patch("openai.OpenAI", return_value=mock_openai_client):
        return OpenAIAdapter(
            api_key="test-api-key",
            model="gpt-3.5-turbo",
            max_tokens=100,
            temperature=0.7,
        )


# OpenAI Adapter Tests
def test_should_generate_text_when_prompt_is_given(
    openai_adapter: OpenAIAdapter, mock_openai_client: Mock
) -> None:
    # Arrange
    prompt = "What is the capital of France?"
    retrieval_context = "The context is about countries and their capitals."

    # Simulate the response from the OpenAI API
    mock_choice = Mock()
    mock_choice.message = Mock(content="The capital of France is Paris.")
    mock_response = Mock(choices=[mock_choice])
    mock_openai_client.chat.completions.create.return_value = mock_response

    # Act
    result = openai_adapter.generate_text(prompt, retrieval_context)

    # Assert
    mock_openai_client.chat.completions.create.assert_called_once_with(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "The context is: The context is about countries and their capitals., please respond to the following question: ",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=100,
        temperature=0.7,
    )
    assert result == "The capital of France is Paris."
