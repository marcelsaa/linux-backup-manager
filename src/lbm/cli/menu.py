from collections.abc import Callable

from lbm.cli.error_handler import ErrorHandler
from lbm.core.application import Application
from lbm.core.errors import ApplicationError
from lbm.services.language import LanguageService
from lbm.ui.console import Console

MenuEntry = tuple[str, Callable[[], object] | None]


class MainMenu:
    """Guided terminal main menu (see docs/ROADMAP.md, Design Philosophy)."""

    def __init__(self, application: Application, language: LanguageService) -> None:
        self.application = application
        self.language = language

    def run(self) -> bool:
        self._show_menu(
            "menu.title",
            [
                ("menu.main.backup", self.application.backup),
                ("menu.main.restore", self.application.restore),
                ("menu.main.status", self.application.status),
                ("menu.main.settings", self.application.settings),
                ("menu.main.administration", self._administration_menu),
                ("menu.main.exit", None),
            ],
        )
        return True

    def _administration_menu(self) -> None:
        self._show_menu(
            "menu.administration.title",
            [
                ("menu.administration.doctor", self.application.doctor),
                ("menu.administration.check", self.application.check),
                ("menu.administration.logs", self.application.view_logs),
                ("menu.administration.history", self.application.snapshots),
                ("menu.administration.repository_info", self.application.recovery_info),
                ("menu.administration.expert", self._expert_menu),
                ("menu.administration.back", None),
            ],
        )

    def _expert_menu(self) -> None:
        self._show_menu(
            "menu.expert.title",
            [
                ("menu.expert.init", self.application.init_repository),
                ("menu.expert.stats", self.application.stats),
                ("menu.expert.forget", self.application.forget),
                ("menu.expert.prune", self.application.prune),
                ("menu.expert.change_password", self.application.change_password),
                ("menu.expert.recovery_sheet", self.application.recovery_sheet),
                ("menu.expert.export_config", self.application.export_config),
                ("menu.expert.import_config", self.application.import_config),
                ("menu.expert.schedule_install", self.application.schedule_install),
                ("menu.expert.schedule_status", self.application.schedule_status),
                ("menu.expert.schedule_remove", self.application.schedule_remove),
                ("menu.expert.back", None),
            ],
        )

    def _show_menu(self, title_key: str, entries: list[MenuEntry]) -> None:
        while True:
            print()
            title = self._text(title_key)
            print(title)
            print("=" * len(title))
            print()
            for index, (label_key, _) in enumerate(entries, start=1):
                print(f"{index}) {self._text(label_key)}")
            print()

            raw = input(self._text("menu.prompt")).strip()
            try:
                choice = int(raw)
            except ValueError:
                Console.error(self._text("menu.invalid_choice"))
                continue

            if choice < 1 or choice > len(entries):
                Console.error(self._text("menu.invalid_choice"))
                continue

            action = entries[choice - 1][1]
            if action is None:
                return
            try:
                action()
            except ApplicationError as error:
                ErrorHandler.show(error)

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)
