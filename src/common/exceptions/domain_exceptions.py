class DomainError(Exception):
    """Base class for domain-level exceptions."""
    pass


class DomainValidationError(DomainError):
    """Raised when domain validation rules are violated."""
    pass
