from cryptography.fernet import Fernet

from settings import settings

_fernet = Fernet(settings.encryption_key)


def encrypt(text: str) -> str:
    return _fernet.encrypt(text.encode()).decode()


def decrypt(token: str) -> str:
    return _fernet.decrypt(token.encode()).decode()
