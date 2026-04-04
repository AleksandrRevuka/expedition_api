from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from src.conf.security_conf import get_jwt_config
from src.conf.logging_config import LOGGER
from fastapi import HTTPException, status


class TokenService:
    """Service for JWT token generation and verification.

    Implements the TokenServicePort interface.
    Does not manage Redis persistence — that is the handler's responsibility.
    """

    def __init__(self) -> None:
        """Initialize the token service with JWT configuration."""
        self.secret_key = get_jwt_config().JWT_TOKEN_SECRET_KEY
        self.algorithm = get_jwt_config().JWT_TOKEN_ALGORITHM

    def create_access_token(self, email: str) -> str:
        """Create a JWT access token for a user.

        Args:
            email: The user's email address (encoded as 'sub')

        Returns:
            The encoded JWT access token string
        """
        data: dict[str, Any] = {"sub": email}
        expire = datetime.now(UTC) + timedelta(
            minutes=get_jwt_config().JWT_ACCESS_TOKEN_EXPIRE_MINS
        )
        data.update({"iat": datetime.now(UTC), "exp": expire, "scope": "access_token"})
        return str(jwt.encode(data, self.secret_key, algorithm=self.algorithm))

    async def get_email_from_token(self, token: str, verify_exp: bool = True) -> str:
        """Decode an email JWT token and return the email encoded in 'sub'.

        Args:
            token: The JWT token string.
            verify_exp: Whether to validate expiry (default True).

        Returns:
            The email address.

        Raises:
            HTTPException 422: If the token is invalid or decoding fails.
        """
        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": verify_exp},
            )
            return str(payload["sub"])
        except JWTError as e:
            LOGGER.error(
                "Invalid token for verification", token_type="email_verification"
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not validate credentials",
            ) from e
