import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pydantic_settings import BaseSettings
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class Settings(BaseSettings):
    secret_key: str = "a-very-secret-fallback-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()

# Setup the HTTP Bearer scheme for Swagger and dependency injection
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    # Convert password to bytes, generate salt, and create the hash
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)

    # Return as a decoded string for easy storage
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Convert both the plain password and the stored hash to bytes for comparison
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")

    # Check if the provided password matches the hash
    return bcrypt.checkpw(
        password=password_byte_enc, hashed_password=hashed_password_bytes
    )


def create_access_token(data: dict) -> str:
    # Create a copy of the data to avoid modifying the original payload
    to_encode = data.copy()

    # Set expiration time for the token
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})

    # Encode and return the JWT
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Validates the token from the request header and returns the user's email.
    If the token is missing or invalid, raises a 401 error.
    """
    token = credentials.credentials
    try:
        # Decode the token using our secret key
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_optional),
) -> str | None:
    """
    Checks if a token exists. If yes -> returns email. If no -> returns None (guest).
    """
    if not credentials:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload.get("sub")
    except JWTError:
        return None
