from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError

from lbm.core.errors import ConfigurationError


class SystemConfig(BaseModel):
    host_name: str


class PathsConfig(BaseModel):
    log_dir: str
    state_dir: str
    password_file: str


class USBTargetConfig(BaseModel):
    enabled: bool
    label: str
    repository_path: str


class TargetsConfig(BaseModel):
    usb: USBTargetConfig


class BackupConfig(BaseModel):
    paths: list[str]
    excludes: list[str]

class RetentionConfig(BaseModel):
    keep_daily: int
    keep_weekly: int
    keep_monthly: int
    keep_yearly: int

class AppConfig(BaseModel):
    system: SystemConfig
    paths: PathsConfig
    targets: TargetsConfig
    backup: BackupConfig
    retention: RetentionConfig


class ConfigLoader:
    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file

    def load(self) -> AppConfig:
        try:
            with self.config_file.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
        except FileNotFoundError as error:
            raise ConfigurationError(
                "Konfigurationsdatei nicht gefunden.",
                hint="Bitte führen Sie zuerst 'backup-manager setup' aus.",
            ) from error
        except IsADirectoryError as error:
            raise ConfigurationError(
                "Konfigurationspfad ist ein Verzeichnis, keine Datei.",
                hint=f"Erwartet wird eine YAML-Datei: {self.config_file}",
            ) from error
        except PermissionError as error:
            raise ConfigurationError(
                "Konfigurationsdatei kann nicht gelesen werden.",
                hint=f"Bitte prüfen Sie die Dateirechte von {self.config_file}.",
            ) from error
        except yaml.YAMLError as error:
            raise ConfigurationError(
                "Konfigurationsdatei ist ungültig.",
                hint=f"Bitte prüfen Sie die YAML-Syntax in {self.config_file}.",
            ) from error

        try:
            return AppConfig.model_validate(data)
        except ValidationError as error:
            details = [
                f"{'.'.join(str(value) for value in item['loc'])}: {item['msg']}"
                for item in error.errors()
            ]
            raise ConfigurationError(
                "Konfigurationsdatei ist unvollständig oder ungültig.",
                details=details,
            ) from error
    
