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


class InvalidRequestError(IgarException):
    """Raised when the API request payload is malformed or incomplete."""

    status_code = 400
    error_type = "invalid_request"


class AuthenticationFailedError(IgarException):
    """Raised when credentials or authentication state are invalid."""

    status_code = 401
    error_type = "invalid_credentials"


class OTPInvalidError(IgarException):
    """Raised when a provided OTP code is invalid."""

    status_code = 401
    error_type = "otp_invalid"


class OTPAlreadySetupError(IgarException):
    """Raised when OTP setup is requested for an already configured account."""

    status_code = 400
    error_type = "otp_already_setup"


class OTPSetupRequiredError(IgarException):
    """Raised when OTP verification is requested before setup."""

    status_code = 400
    error_type = "otp_setup_required"


class OTPChallengeInvalidError(IgarException):
    """Raised when a login challenge token is invalid or expired."""

    status_code = 401
    error_type = "otp_challenge_invalid"


class OTPRateLimitedError(IgarException):
    """Raised when OTP verification attempts exceed configured limits."""

    status_code = 429
    error_type = "otp_rate_limited"


class CaptureUnsupportedFileTypeError(IgarException):
    """Raised when capture receives a file type outside supported MIME list."""

    status_code = 422
    error_type = "capture_unsupported_file_type"


class CaptureFileTooLargeError(IgarException):
    """Raised when capture receives a file beyond configured upload limit."""

    status_code = 422
    error_type = "capture_file_too_large"
