class ApplicationError(Exception):
    """Expected application error that can be shown without a traceback."""

    def __init__(
        self,
        message: str,
        *,
        hint: str | None = None,
        details: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint
        self.details = details or []


class ConfigurationError(ApplicationError):
    """Configuration could not be loaded or validated."""


class ExternalCommandError(ApplicationError):
    """An external program could not be started."""
