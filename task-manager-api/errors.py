"""Domain errors raised by the service layer and translated to HTTP in app.py."""


class ValidationError(Exception):
    """Input failed a business rule. Mapped to HTTP 422."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.message = message
        self.field = field


class NotFoundError(Exception):
    """Requested record does not exist. Mapped to HTTP 404."""

    def __init__(self, resource: str, resource_id: int):
        super().__init__(f"{resource} {resource_id} not found")
        self.message = f"{resource} {resource_id} not found"
