import getpass
import os
import tempfile
from pathlib import Path

from lbm.core.config import AppConfig
from lbm.core.errors import ApplicationError
from lbm.services.language import LanguageService
from lbm.services.recovery import RecoverySheetService
from lbm.services.repository import RepositoryProvider
from lbm.ui.console import Console
from lbm.utils.prompts import is_yes


class PasswordChangeService:
    def __init__(
        self,
        config: AppConfig,
        config_file: Path,
        repository_provider: RepositoryProvider | None = None,
    ) -> None:
        self.config = config
        self.config_file = config_file
        self.language = LanguageService(config.system.language)
        self.repository_provider = repository_provider or RepositoryProvider(config)

    def run(self) -> bool:
        Console.warning(self._text("password_change.warning"))
        print(self._text("password_change.irreversible"))
        print()

        new_password = getpass.getpass(self._text("password_change.new_password_prompt"))
        if not new_password:
            Console.error(self._text("password_change.empty_password"))
            return False
        confirm = getpass.getpass(self._text("password_change.confirm_prompt"))
        if new_password != confirm:
            Console.error(self._text("password_change.mismatch"))
            return False

        destinations = self.repository_provider.get_all()
        if not destinations:
            Console.error(self._text("password_change.no_destinations"))
            return False

        password_file = Path(self.config.paths.password_file).expanduser()
        changed_names: list[str] = []

        tmp_fd, tmp_str = tempfile.mkstemp()
        tmp_path = Path(tmp_str)
        try:
            os.fchmod(tmp_fd, 0o600)
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                f.write(new_password + "\n")

            for destination in destinations:
                Console.info(self._text("password_change.changing", name=destination.name))
                ok = destination.repository.change_password(tmp_path)
                if not ok:
                    Console.error(self._text("password_change.failed", name=destination.name))
                    if changed_names:
                        Console.warning(
                            self._text(
                                "password_change.partial_change",
                                names=", ".join(changed_names),
                            )
                        )
                    return False
                changed_names.append(destination.name)

            self._update_password_file(password_file, new_password)
        finally:
            tmp_path.unlink(missing_ok=True)

        Console.success(self._text("password_change.success"))
        print()
        answer = input(self._text("password_change.regenerate_sheet_prompt"))
        if is_yes(answer, self._text("common.yes_short")):
            RecoverySheetService(self.config, self.config_file).run()
        else:
            Console.info(self._text("password_change.sheet_reminder"))
        return True

    def _update_password_file(self, password_file: Path, new_password: str) -> None:
        temporary = password_file.with_name(f".{password_file.name}.tmp")
        try:
            password_file.parent.mkdir(parents=True, exist_ok=True)
            temporary.write_text(new_password + "\n", encoding="utf-8")
            temporary.chmod(0o600)
            temporary.replace(password_file)
            password_file.chmod(0o600)
        except OSError as error:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise ApplicationError(
                self._text("password_change.file_update_failed"),
                hint=str(error),
            ) from error

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)
