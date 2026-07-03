from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator
from yaml.constructor import ConstructorError

from lbm.core.errors import ConfigurationError


class UniqueKeyLoader(yaml.SafeLoader):
    """YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key: {key}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


class SystemConfig(BaseModel):
    host_name: str
    language: Literal["de", "en"] = "de"


class PathsConfig(BaseModel):
    log_dir: str
    state_dir: str
    password_file: str


class USBTargetConfig(BaseModel):
    enabled: bool
    label: str
    repository_path: str


class NASTargetConfig(BaseModel):
    enabled: bool = False
    mount_path: str = ""
    repository_path: str = "restic/linux-backup-manager"


class TargetsConfig(BaseModel):
    usb: USBTargetConfig
    nas: NASTargetConfig = Field(default_factory=NASTargetConfig)

    @model_validator(mode="after")
    def require_enabled_target(self) -> "TargetsConfig":
        if not self.usb.enabled and not self.nas.enabled:
            raise ValueError("at least one backup target must be enabled")
        return self


class BackupConfig(BaseModel):
    paths: list[str]
    excludes: list[str]

class RetentionConfig(BaseModel):
    keep_daily: int = 14
    keep_weekly: int = 8
    keep_monthly: int = 12
    keep_yearly: int = 3


class ScheduleConfig(BaseModel):
    enabled: bool = False
    daily_time: str = "20:00"
    interval_days: int = Field(default=1, ge=1, le=365)
    boot_delay_minutes: int = Field(default=2, ge=1)


class AppConfig(BaseModel):
    system: SystemConfig
    paths: PathsConfig
    targets: TargetsConfig
    backup: BackupConfig
    retention: RetentionConfig
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)


class ConfigLoader:
    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file

    def load(self) -> AppConfig:
        try:
            with self.config_file.open("r", encoding="utf-8") as file:
                data = yaml.load(file, Loader=UniqueKeyLoader)
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

    def detect_language(self) -> str | None:
        try:
            with self.config_file.open("r", encoding="utf-8") as file:
                data = yaml.load(file, Loader=UniqueKeyLoader)
        except (OSError, yaml.YAMLError):
            return None
        if not isinstance(data, dict):
            return None
        system = data.get("system")
        if not isinstance(system, dict):
            return None
        language = system.get("language")
        return language if language in ("de", "en") else None
