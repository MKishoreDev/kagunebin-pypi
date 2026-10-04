class KaguneBinError(Exception):
    """Base exception for all KaguneBin errors."""
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class KaguneBinAuthError(KaguneBinError):
    """Raised when authentication fails (401 - password required or incorrect)."""
    pass


class KaguneBinNotFoundError(KaguneBinError):
    """Raised when a paste is not found (404)."""
    pass


class KaguneBinExpiredError(KaguneBinError):
    """Raised when a paste has expired or has already been burned (410)."""
    pass


class KaguneBinValidationError(KaguneBinError):
    """Raised when request validation fails (400 or 422 - invalid syntax, payload size, etc.)."""
    pass


class KaguneBinConnectionError(KaguneBinError):
    """Raised when connection to KaguneBin fails or times out."""
    pass


class KaguneBinAPIError(KaguneBinError):
    """Raised when the KaguneBin server returns a 5xx error."""
    pass
