from app.core import ports, models
from pymongo import MongoClient
from app.core.models import Document, User


class MongoDbAdapter(ports.DatabasePort):
    def __init__(self, url: str) -> None:
        self.client = MongoClient(url)
        #nombre de la base de datos
        self.db = self.client["rag_db"]
        #nombre de las colecciones
        self.users = self.db["users"]
        self.documents = self.db["documents"]

    def save_user(self, user: User) -> None:
        self.users.insert_one({
            "uid": user.uid,
            "username": user.username,
            "password": user.password,
            "is_admin": user.is_admin})

    def get_user(self, uid: str) -> models.User:
        user = self.users.find_one({"uid": uid})
        return models.User(uid=user["uid"],
                           username=user["username"],
                           password=user["password"],
                           is_admin=user["is_admin"])

    def update_user_role(self, uid: str, is_admin: bool) -> None:
            result = self.users.update_one({"uid": uid}, {"$set": {"is_admin": is_admin}})

    def save_document(self, document: models.Document) -> None:
        self.documents.insert_one({"document_id": document.document_id, "nombre": document.nombre})

    def get_document(self, document_id: str) -> Document | None:
        document = self.documents.find_one({"document_id": document_id})
        if document:
            return models.Document(document_id=document["document_id"], nombre=document["nombre"], ruta=document["ruta"])
        return None