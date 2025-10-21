import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# Backend padrão para operações criptográficas
_backend = default_backend()

def _derive_key(password: str, salt: bytes) -> bytes:
    """
    Deriva uma chave criptográfica segura a partir de uma senha e um salt.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,  # Número de iterações recomendado
        backend=_backend
    )
    # A chave Fernet deve ter 32 bytes e ser codificada em base64
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt(message: str, password: str) -> bytes:
    """
    Criptografa uma mensagem usando uma senha.
    Retorna um 'token' (salt + mensagem cifrada).
    """
    # 1. Gera um salt aleatório para cada nova mensagem
    salt = os.urandom(16)
    
    # 2. Deriva a chave a partir da senha e do salt
    key = _derive_key(password, salt)
    
    # 3. Criptografa a mensagem
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    
    # 4. Retorna o salt + a mensagem cifrada. 
    # Precisamos do salt para descriptografar.
    return salt + encrypted_message

def decrypt(token: bytes, password: str) -> str | None:
    """
    Descriptografa um token (salt + mensagem) usando uma senha.
    Retorna a mensagem original se a senha estiver correta, ou None se falhar.
    """
    try:
        # 1. Extrai o salt (primeiros 16 bytes)
        salt = token[:16]
        
        # 2. Extrai a mensagem cifrada (o resto)
        encrypted_message = token[16:]
        
        # 3. Deriva a chave (deve ser o mesmo processo da criptografia)
        key = _derive_key(password, salt)
        
        # 4. Tenta descriptografar
        f = Fernet(key)
        decrypted_message = f.decrypt(encrypted_message)
        
        return decrypted_message.decode()
        
    except InvalidToken:
        # Erro mais comum: a chave (senha) está incorreta.
        return None
    except Exception as e:
        # Outros erros (ex: dados corrompidos)
        print(f"Erro inesperado ao descriptografar: {e}")
        return None