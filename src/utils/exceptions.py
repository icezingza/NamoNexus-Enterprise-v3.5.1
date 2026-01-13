"""Custom exception types for NamoNexus."""


class NamoException(Exception):
    """Base exception for application errors."""


class UserNotFoundError(NamoException):
    """Raised when a user is not found."""


class InvalidInputError(NamoException):
    """Raised when input validation fails."""


class SafetyException(NamoException):
    """Raised when safety checks fail."""


class DatabaseError(NamoException):
    """Raised when database operations fail."""


class ServiceError(NamoException):
    """Raised when a service fails to complete."""


class RateLimitExceeded(NamoException):
    """Raised when a rate limit is exceeded."""
