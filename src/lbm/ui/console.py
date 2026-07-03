import logging


class Console:
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    RESET = "\033[0m"

    @staticmethod
    def success(text: str) -> None:
        print(f"{Console.GREEN}✓ {text}{Console.RESET}")
        logging.info(text)

    @staticmethod
    def error(text: str) -> None:
        print(f"{Console.RED}✗ {text}{Console.RESET}")
        logging.error(text)

    @staticmethod
    def warning(text: str) -> None:
        print(f"{Console.YELLOW}! {text}{Console.RESET}")
        logging.warning(text)

    @staticmethod
    def info(text: str) -> None:
        print(f"{Console.BLUE}{text}{Console.RESET}")
        logging.info(text)

    @staticmethod
    def headline(text: str) -> None:
        print(f"\n{Console.BLUE}{text}{Console.RESET}")
        logging.info(text)

    @staticmethod
    def separator() -> None:
        print("-" * 60)