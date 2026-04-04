class UserNotFoundError(Exception):
    """Raised when a user is not found."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class UserAlreadyExistsError(Exception):
    """Raised when a user already exists."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidCredentialsError(Exception):
    """Raised when invalid credentials are provided."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
