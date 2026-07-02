import shutil
from pathlib import Path

import yaml
from pydantic import ValidationError

from lbm.core.config import AppConfig, UniqueKeyLoader
from lbm.services.language import LanguageService
from lbm.ui.console import Console
from lbm.utils.prompts import is_yes


class ConfigExportService:
    """Copy the current configuration file to a user-chosen destination."""

    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file
        self.language = LanguageService(self._detect_language())

    def _detect_language(self) -> str:
        try:
            with self.config_file.open(encoding="utf-8") as f:
                data = yaml.load(f, Loader=UniqueKeyLoader)
            return (data or {}).get("system", {}).get("language") or "de"
        except Exception:
            return "de"

    def run(self) -> bool:
        title = self._text("config_transfer.export_title")
        print(title)
        print("=" * len(title))
        print()

        if not self.config_file.is_file():
            Console.error(self._text("config_transfer.export_no_config"))
            return False

        default = Path.home() / "lbm-config-backup.yaml"
        raw = input(self._text("config_transfer.export_destination", default=default)).strip()
        destination = Path(raw).expanduser() if raw else default

        if destination.is_file():
            answer = input(self._text("config_transfer.export_overwrite", path=destination))
            if not is_yes(answer, self._text("common.yes_short")):
                Console.warning(self._text("config_transfer.export_not_overwritten"))
                return False

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.config_file, destination)
        Console.success(self._text("config_transfer.export_success", path=destination))
        return True

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)


class ConfigImportService:
    """Validate and install a configuration file from a user-chosen source."""

    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file
        self.language = LanguageService(self._detect_language())

    def _detect_language(self) -> str:
        try:
            with self.config_file.open(encoding="utf-8") as f:
                data = yaml.load(f, Loader=UniqueKeyLoader)
            return (data or {}).get("system", {}).get("language") or "de"
        except Exception:
            return "de"

    def run(self) -> bool:
        title = self._text("config_transfer.import_title")
        print(title)
        print("=" * len(title))
        print()

        raw = input(self._text("config_transfer.import_source")).strip()
        source = Path(raw).expanduser()

        if not source.is_file():
            Console.error(self._text("config_transfer.import_source_not_found", path=source))
            return False

        try:
            with source.open(encoding="utf-8") as f:
                data = yaml.load(f, Loader=UniqueKeyLoader)
            AppConfig.model_validate(data)
        except (ValidationError, yaml.YAMLError) as error:
            Console.error(self._text("config_transfer.import_invalid", error=error))
            return False

        if self.config_file.is_file():
            backup = Path(str(self.config_file) + ".bak")
            shutil.copy2(self.config_file, backup)
            Console.info(self._text("config_transfer.import_backup_created", path=backup))

        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.config_file.with_name(f".{self.config_file.name}.tmp")
        shutil.copy2(source, tmp)
        tmp.replace(self.config_file)
        Console.success(self._text("config_transfer.import_success", path=self.config_file))
        return True

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)
