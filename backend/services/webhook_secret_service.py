import hashlib
import hmac
import secrets

# Not the password hasher: password hasher algorithm is salted, so the same secret never gives the same hash
# and the webhook's user could not be found by hash. The secret is 256 random bits, so a
# fast, deterministic hash is enough.


def generate_webhook_secret() -> str:
    return secrets.token_urlsafe(32)


def hash_webhook_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def verify_webhook_secret(secret: str, secret_hash: str) -> bool:
    return hmac.compare_digest(hash_webhook_secret(secret), secret_hash)
