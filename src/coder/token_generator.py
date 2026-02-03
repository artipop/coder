import hashlib
import hmac

# TODO: use env!!!
SECRET_SALT = b"super-secret-salt"

def generate_token(identifier: str) -> str:
    digest = hmac.new(SECRET_SALT, identifier.encode(), hashlib.sha256).hexdigest()
    return f"sk-{digest[:32]}"
