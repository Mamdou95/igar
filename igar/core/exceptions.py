"""Igar business exceptions."""


class IgarException(Exception):
    """Base exception for all Igar business errors."""

    status_code = 500
    error_type = "internal_error"

    def __init__(self, detail=None, **kwargs):
        self.detail = detail or self.error_type
        self.extra = kwargs
        super().__init__(self.detail)


class DocumentProtectedError(IgarException):
    """Raised when attempting to modify or delete a WORM-protected document."""

    status_code = 403
    error_type = "document_protected"


class IntegrityViolationError(IgarException):
    """Raised when document integrity verification fails."""

    status_code = 409
    error_type = "integrity_violation"


class ClassificationFailedError(IgarException):
    """Raised when AI classification fails to process a document."""

    status_code = 422
    error_type = "classification_failed"
