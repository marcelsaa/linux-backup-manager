from pathlib import Path

import yaml
from pydantic import BaseModel


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

class AppConfig(BaseModel):
    system: SystemConfig
    paths: PathsConfig
    targets: TargetsConfig
    backup: BackupConfig


class ConfigLoader:
    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file

    def load(self) -> AppConfig:
        with self.config_file.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        return AppConfig.model_validate(data)