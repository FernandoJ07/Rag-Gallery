from app.adapters.openai_adapter import OpenAIAdapter
from app.adapters.chromadb_adapter import ChromaDBAdapter
from app.adapters.database_adapter import MongoDbAdapter
from app import usecases
from app import configurations


class RAGServiceSingleton:
    _instance = None

    @classmethod
    def get_instance(cls) -> usecases.RAGService:
        if cls._instance is None:
            configs = configurations.Configs()
            openai_adapter = OpenAIAdapter(
                api_key=configs.openai_api_key,
                model=configs.model,
                max_tokens=configs.max_tokens,
                temperature=configs.temperature,
            )
            document_repo = ChromaDBAdapter(
                number_of_vectorial_results=configs.number_of_vectorial_results
            )
            database_adapter = MongoDbAdapter(
                url=configs.url_mongodb, db_name=configs.db_name
            )
            cls._instance = usecases.RAGService(
                document_repo=document_repo,
                openai_adapter=openai_adapter,
                db=database_adapter,
            )

        return cls._instance
