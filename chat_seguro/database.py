import pymongo
from pymongo.errors import ConnectionFailure
from datetime import datetime
from bson import ObjectId # Para buscar por _id

class DatabaseManager:
    """
    Classe responsável por gerenciar a conexão e 
    operações com o banco de dados MongoDB.
    """
    def __init__(self, connection_string="mongodb://localhost:27017/"):
        try:
            self.client = pymongo.MongoClient(connection_string)
            # Testa a conexão
            self.client.admin.command('ping')
            print("Conexão com o MongoDB estabelecida com sucesso.")
        except ConnectionFailure as e:
            print(f"Erro ao conectar ao MongoDB: {e}")
            raise
            
        # Define o banco de dados e as coleções
        self.db = self.client["chat_seguro"]
        self.users_collection = self.db["Users"]
        self.messages_collection = self.db["Messages"]
        
        # Opcional: Pré-popular usuários se não existirem
        self._setup_initial_users()

    def _setup_initial_users(self):
        """
        Adiciona alguns usuários de exemplo se a coleção estiver vazia.
        Isso ajuda nos testes, já que não há tela de cadastro.
        """
        if self.users_collection.count_documents({}) == 0:
            print("Populando coleção 'Users' com usuários de exemplo...")
            self.users_collection.insert_many([
                {"username": "@alice"},
                {"username": "@bob"},
                {"username": "@charlie"}
            ])

    def send_message(self, sender: str, recipient: str, encrypted_message: bytes):
        """
        Salva a mensagem criptografada no banco.
        """
        message_doc = {
            "sender": sender,
            "recipient": recipient,
            "message": encrypted_message, # Armazena como dados binários (BSON)
            "timestamp": datetime.now(),
            "status": "não lida"
        }
        self.messages_collection.insert_one(message_doc)
        print(f"Mensagem para {recipient} enviada com sucesso!")

    def get_unread_messages(self, recipient: str) -> list:
        """
        Busca mensagens não lidas para um usuário, ordenadas da mais nova.
        """
        cursor = self.messages_collection.find(
            {"recipient": recipient, "status": "não lida"}
        ).sort("timestamp", pymongo.DESCENDING)
        
        return list(cursor)

    def mark_message_as_read(self, message_id: ObjectId):
        """
        Atualiza o status de uma mensagem para 'lida'.
        """
        self.messages_collection.update_one(
            {"_id": message_id},
            {"$set": {"status": "lida"}}
        )
        print("Mensagem marcada como lida.")

    def close_connection(self):
        """Fecha a conexão com o banco."""
        self.client.close()
        print("Conexão com o MongoDB fechada.")