"""Custom exceptions for pygreat."""


class GreatError(Exception):
    """Base exception for GREAT-related errors."""

    pass


class InvalidSpeciesError(GreatError):
    """Raised when an unsupported species is specified."""

    pass


class InvalidRegionsError(GreatError):
    """Raised when input regions are invalid."""

    pass


class RateLimitError(GreatError):
    """Raised when GREAT rate limit is exceeded.

    Attributes:
        retry_after: Suggested wait time in seconds before retrying.
    """

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class JobNotFoundError(GreatError):
    """Raised when a job session is not found on the server."""

    pass


class ParsingError(GreatError):
    """Raised when response parsing fails."""

    pass


class ConnectionError(GreatError):
    """Raised when connection to GREAT server fails."""

    pass
