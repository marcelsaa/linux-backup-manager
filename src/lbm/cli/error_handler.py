from lbm.core.errors import ApplicationError
from lbm.ui.console import Console


class ErrorHandler:
    """Render expected application errors consistently for the CLI."""

    @staticmethod
    def show(error: ApplicationError) -> None:
        Console.error(error.message)
        if error.hint:
            Console.info(error.hint)
        for detail in error.details:
            Console.info(detail)
