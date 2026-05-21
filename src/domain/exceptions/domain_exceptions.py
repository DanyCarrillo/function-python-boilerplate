class DomainException(Exception):
    """Base domain exception."""


class EntityNotFoundException(DomainException):
    """Raised when an entity is not found."""


class ValidationException(DomainException):
    """Raised when a validation error occurs."""


class IntegrationException(DomainException):
    """Raised when an external integration fails."""
