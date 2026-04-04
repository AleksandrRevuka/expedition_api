from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class PasswordService:
    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def hash(self, password: str) -> str:
        """Hash a plaintext password using Argon2.

        Args:
            password: The plaintext password to hash

        Returns:
            The hashed password string
        """
        hashed = self._hasher.hash(password)
        return hashed

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify that a plaintext password matches a hashed password.

        Args:
            plain_password: The plaintext password to verify
            hashed_password: The hashed password to compare against

        Returns:
            True if passwords match, False otherwise
        """
        try:
            self._hasher.verify(hashed_password, plain_password)
            return True
        except VerifyMismatchError:
            return False
