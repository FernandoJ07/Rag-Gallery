import chromadb
import numpy as np
from typing import List, Optional
from app.core import ports, models
from app.helpers.vectorize_documents import document_to_vectors, get_openai_embeddings
from app.adapters.openai_adapter import OpenAIAdapter  # Importamos OpenAIAdapter


class ChromaDBAdapter(ports.DocumentRepositoryPort):
    def __init__(self, number_of_vectorial_results: int) -> None:
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("documents")
        self._number_of_vectorial_results = number_of_vectorial_results

    # Guardar un documento con embeddings generados por OpenAI
    def save_document(
        self,
        document: models.Document,
        content: Optional[str],
        openai_client: object,  # Mantenemos object para cumplir con la superclase
    ) -> None:
        if content is None:
            raise ValueError("El contenido no puede ser None")
        if not isinstance(openai_client, OpenAIAdapter):
            raise TypeError("openai_client debe ser una instancia de OpenAIAdapter")

        embeddings_document = document_to_vectors(content, openai_client)

        # Si hay más de un embedding, combinarlo promediando
        if len(embeddings_document) > 1:
            combined_embedding = np.mean(embeddings_document, axis=0).tolist()
        else:
            combined_embedding = embeddings_document[0]

        # Agregar el documento a ChromaDB con su embedding
        self.collection.add(
            ids=[document.document_id],
            embeddings=[
                combined_embedding
            ],  # Aseguramos que sea una lista de embeddings
            documents=[content],
        )

    # Obtener documentos usando embeddings generados para la query
    def get_documents(
        self,
        query: str,
        openai_client: object,
        n_results: Optional[
            int
        ] = None,  # Mantenemos object para cumplir con la superclase
    ) -> List[models.Document]:
        if not isinstance(openai_client, OpenAIAdapter):
            raise TypeError("openai_client debe ser una instancia de OpenAIAdapter")

        if not n_results:
            n_results = self._number_of_vectorial_results

        # Generar embedding para la query usando OpenAI
        query_embedding = get_openai_embeddings(query, openai_client)

        # Hacer la consulta usando los embeddings de la query
        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )

        # Procesar los resultados y devolver documentos
        documents = []
        for i, doc_id_list in enumerate(results["ids"]):
            for doc_id in doc_id_list:
                documents.append(
                    models.Document(id=doc_id, content=results["documents"][i][0])
                )
        return documents

    # Obtener vectores almacenados en la colección
    def get_vectors(self) -> dict:
        data = self.collection.get(include=["embeddings", "documents"])

        data_formateada = {
            "ids": data.get("ids", []),
            "embeddings": (
                data.get("embeddings", []).tolist()
                if data.get("embeddings") is not None
                else None
            ),  # Convierte a lista si es un array
            "documents": data.get("documents", []),
        }

        return data_formateada
