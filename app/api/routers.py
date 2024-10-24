from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app import usecases
from app.api import dependencies
from app.usecases import UserRequest, QueryRequest, UpdateRoleUserRequest

rag_router = APIRouter()

@rag_router.post("/save-document/", status_code=201)
def save_document(file: UploadFile = File(...),
                        rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    # Guardar la información del archivo en MongoDB
    rag_service.save_document(file)
    return {"status": "Document saved successfully"}

@rag_router.post("/generate-answer/", status_code=201)
def generate_answer(query_data: QueryRequest,
                    rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    return rag_service.generate_answer(query_data)

# @rag_router.get("/get-document/")
# def get_document(document_id: str,
#                  rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
#     document = rag_service.get_document(document_id)
#     if document:
#         return document
#     return {"status": "Document not found"}

# @rag_router.get("/get-vectors/", status_code=201)
# def get_vectors(rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
#     return rag_service.get_vectors()

@rag_router.post("/sign-up/", status_code=201)
def sing_up(user_request: UserRequest,
            rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    rag_service.sign_up(user_request)
    return {"status": "Usuario registrado exitosamente"}

@rag_router.get("/get-user/")
def get_user(username: str,
             rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    user = rag_service.get_user(username)
    if user:
        return user
    return {"status": "Usuario no encontrado"}

@rag_router.get("/get-users/")
def get_users(rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    return rag_service.get_users()

@rag_router.patch("/change-role/")
def update_role(user: UpdateRoleUserRequest,
                rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)):
    rag_service.update_role(user)
    return {"status": "Role actualizado exitosamente"}


@rag_router.post("/login/")
def login_for_access_token(
        user_request: UserRequest,
        rag_service: usecases.RAGService = Depends(dependencies.RAGServiceSingleton.get_instance)
):
    # Llama a la función de autenticación usando el nombre de usuario y la contraseña
    user = rag_service.authenticate_user(user_request.username, user_request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crea el token de acceso
    access_token = usecases.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}




