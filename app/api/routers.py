from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app import usecases
from app.api import dependencies
from app.core.models import User
from app.usecases import UserRequest, QueryRequest, UpdateRoleUserRequest
from app.helpers.auth import (
    oauth2_scheme,
    decode_access_token,
)
from typing import Dict, Union, List, Any

rag_router = APIRouter()


@rag_router.post("/save-document/", status_code=201)
def save_document(
    file: UploadFile = File(...),
    rag_service: usecases.RAGService = Depends(
        dependencies.RAGServiceSingleton.get_instance
    ),
) -> Dict[str, str]:  # Añadimos el tipo de retorno
    rag_service.save_document(file)
    return {"status": "Document saved successfully"}


@rag_router.post("/generate-answer/", status_code=201)
def generate_answer(
    query_data: QueryRequest,
    rag_service: usecases.RAGService = Depends(
        dependencies.RAGServiceSingleton.get_instance
    ),
) -> Dict[str, Union[str, List[Any]]]:  # Ajustamos el tipo de retorno
    result = rag_service.generate_answer(query_data)
    if isinstance(result, str):
        return {
            "answer": result
        }  # Aseguramos que el retorno siempre sea un diccionario
    return {"answer": result}


@rag_router.get("/get-user/")
def get_user(
    username: str,
    rag_service: usecases.RAGService = Depends(
        dependencies.RAGServiceSingleton.get_instance
    ),
) -> User | dict[str, str]:
    user = rag_service.get_user(username)
    if user:
        return user
    return {"status": "Usuario no encontrado"}


@rag_router.get("/get-users/")
def get_users(
    rag_service: usecases.RAGService = Depends(
        dependencies.RAGServiceSingleton.get_instance
    ),
) -> list:
    return rag_service.get_users()


@rag_router.patch("/change-role/")
def update_role(
    user: UpdateRoleUserRequest,
    rag_service: usecases.RAGService = Depends(
        dependencies.RAGServiceSingleton.get_instance
    ),
) -> Dict[str, str]:
    rag_service.update_role(user)
    return {"status": "Role actualizado exitosamente"}


@rag_router.post("/sign-up/", status_code=201)
def sign_up(
    user_request: UserRequest,
    rag_service: usecases.RAGService = Depends(
        dependencies.RAGServiceSingleton.get_instance
    ),
) -> Dict[str, str]:
    rag_service.sign_up(user_request)

    access_token = rag_service.authenticate_user(
        user_request.username, user_request.password
    )
    return {"access_token": access_token or "", "token_type": "bearer"}


@rag_router.post("/login/")
def login_for_access_token(
    user_request: UserRequest,
    rag_service: usecases.RAGService = Depends(
        dependencies.RAGServiceSingleton.get_instance
    ),
) -> Dict[str, str]:
    access_token = rag_service.authenticate_user(
        user_request.username, user_request.password
    )
    return {"access_token": access_token or "", "token_type": "bearer"}


@rag_router.get("/session-status/")
def session_status(token: str = Depends(oauth2_scheme)) -> Dict[str, Union[str, int]]:
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    # Aseguramos que "user_id" sea un str o int, no None
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )

    return {"status": "Sesión activa", "user_id": user_id}
