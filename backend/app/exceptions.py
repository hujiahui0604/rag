"""Custom exceptions"""


class NotFoundError(Exception):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: int):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} with id {resource_id} not found")


class ValidationError(Exception):
    """Validation error."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnsupportedFileTypeError(Exception):
    """Unsupported file type."""

    def __init__(self, file_type: str):
        self.file_type = file_type
        super().__init__(f"Unsupported file type: {file_type}")


class PermissionDeniedError(Exception):
    """Permission denied."""

    def __init__(self, message: str = "Permission denied"):
        self.message = message
        super().__init__(message)