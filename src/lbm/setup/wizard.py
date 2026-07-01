import os
from datetime import datetime
from getpass import getpass
from importlib.resources import files
from pathlib import Path
from shutil import copy2, which
from socket import gethostname

import yaml

from lbm.backup.restic import RepositoryStatus
from lbm.core.config import AppConfig, ConfigLoader, UniqueKeyLoader
from lbm.core.errors import ApplicationError
from lbm.services.language import LanguageService
from lbm.services.repository import RepositoryDestination, RepositoryProvider
from lbm.services.scheduler import SystemdScheduler
from lbm.targets.usb import USBTarget
from lbm.ui.console import Console
from lbm.utils.prompts import is_yes


class SetupWizard:
    def __init__(self, config_file: Path, interactive: bool = True) -> None:
        self.config_file = config_file
        self.password_file = Path()
        self.config: AppConfig | None = None
        self.interactive = interactive
        self.language = LanguageService()
        self.language_preselected = False

    def _load_setup_config(self) -> bool:
        try:
            self.config = ConfigLoader(self.config_file).load()
        except ApplicationError as error:
            Console.error(self._text("setup.config_load_failed"))
            Console.error(error.message)
            if error.hint:
                Console.info(error.hint)
            for detail in error.details:
                Console.info(detail)
            return False

        self.password_file = Path(self.config.paths.password_file).expanduser()
        self.language = LanguageService(self.config.system.language)
        return True

    def _print_header(self) -> None:
        title = self._text("setup.title")
        print(title)
        print("=" * len(title))
        print()
        print(self._text("setup.welcome"))
        print()

    def _print_summary(self, all_ok: bool) -> None:
        print()
        if all_ok:
            Console.success(self._text("setup.complete"))
        else:
            Console.warning(self._text("setup.incomplete"))

    def _check_config(self) -> bool:
        if self.config_file.exists():
            Console.success(self._text("setup.config_present"))
            if not self.interactive:
                return True
            answer = input(
                self._text(
                    "setup.edit_existing",
                    suffix=self._text("common.no_default_suffix"),
                )
            )
            if not is_yes(answer, self._text("common.yes_short")):
                return True
            return self._edit_config()

        Console.error(self._text("setup.config_missing"))
        if not self.interactive:
            Console.warning(self._text("setup.config_creation_skipped"))
            return False

        answer = input(
            self._text(
                "setup.create_default_config",
                suffix=self._text("common.yes_default_suffix"),
            )
        )
        if answer.strip() and not is_yes(answer, self._text("common.yes_short")):
            print(self._text("setup.config_not_created"))
            return False

        try:
            template = files("lbm.resources").joinpath("config.example.yaml")
            data = yaml.safe_load(template.read_text(encoding="utf-8"))
        except (FileNotFoundError, yaml.YAMLError):
            Console.error(self._text("setup.default_config_load_failed"))
            return False

        if self.language_preselected:
            data["system"]["language"] = self.language.language
        else:
            self._configure_language(data)
        data["system"]["host_name"] = gethostname()
        if not self._configure_and_confirm(data):
            return False

        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self._write_config(data)
        Console.success(self._text("setup.config_created"))
        return True

    def _edit_config(self) -> bool:
        try:
            ConfigLoader(self.config_file).load()
            data = yaml.load(
                self.config_file.read_text(encoding="utf-8"),
                Loader=UniqueKeyLoader,
            )
        except ApplicationError as error:
            Console.error(error.message)
            if error.hint:
                Console.info(error.hint)
            for detail in error.details:
                Console.info(detail)
            return False
        except (OSError, yaml.YAMLError) as error:
            Console.error(self._text("setup.config_edit_failed", error=error))
            return False

        print()
        Console.info(self._text("setup.reconfigure_info"))
        self._configure_language(data)
        if not self._configure_and_confirm(data, data["backup"]["paths"]):
            return False

        try:
            AppConfig.model_validate(data)
            backup_file = self.config_file.with_name(f"{self.config_file.name}.bak")
            copy2(self.config_file, backup_file)
            self._write_config(data)
        except (OSError, ValueError, yaml.YAMLError) as error:
            Console.error(self._text("setup.config_save_failed", error=error))
            return False

        Console.success(self._text("setup.config_updated"))
        Console.info(self._text("setup.config_backup", path=backup_file))
        return True

    def _write_config(self, data: dict) -> None:
        temporary_file = self.config_file.with_name(f".{self.config_file.name}.tmp")
        temporary_file.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        temporary_file.replace(self.config_file)

    def _ask_yes_no(self, prompt: str, default: bool) -> bool:
        suffix = self._text(
            "common.yes_default_suffix" if default else "common.no_default_suffix"
        )
        answer = input(f"{prompt} {suffix}: ").strip().lower()
        if not answer:
            return default
        return is_yes(answer, self._text("common.yes_short"))

    def _configure_language(
        self,
        data: dict,
        prompt_key: str = "language.selection_prompt",
    ) -> None:
        system = data.setdefault("system", {})
        current = system.get("language", LanguageService.default_language)
        language = LanguageService(current)

        while True:
            prompt = language.translate(prompt_key)
            selected = input(f"{prompt} [{current}]: ").strip().lower() or current
            if selected in LanguageService.supported_languages:
                system["language"] = selected
                self.language = LanguageService(selected)
                confirmation = self.language.translate(
                    "language.selected",
                    language=selected,
                )
                Console.info(confirmation)
                return
            Console.error(language.translate("language.invalid"))

    def _ask_backup_paths(self, current_paths: list[str] | None = None) -> list[str]:
        default_paths = [
            "~/Dokumente",
            "~/Bilder",
            "~/Schreibtisch",
            "~/Downloads",
            "~/Projekte",
        ]
        print()
        print(self._text("setup.select_standard_folders"))
        print()

        selected_paths = []
        for path in default_paths:
            default = current_paths is None or path in current_paths
            if self._ask_yes_no(self._text("setup.backup_path", path=path), default):
                selected_paths.append(path)

        custom_paths = [path for path in current_paths or [] if path not in default_paths]
        if custom_paths:
            print()
            print(self._text("setup.existing_custom_folders"))
            for path in custom_paths:
                if self._ask_yes_no(
                    self._text("setup.keep_backup_path", path=path), True
                ):
                    selected_paths.append(path)

        print()
        print(self._text("setup.add_custom_folders"))
        print(self._text("setup.empty_finishes"))
        print()
        while value := input(self._text("setup.additional_folder")).strip():
            selected_paths.append(value)

        if not selected_paths:
            Console.error(self._text("setup.folder_required"))
            return self._ask_backup_paths()
        return selected_paths

    def _configure_and_confirm(
        self,
        data: dict,
        current_paths: list[str] | None = None,
    ) -> bool:
        while True:
            data["backup"]["paths"] = self._ask_backup_paths(current_paths)
            if not self._configure_targets(data):
                return False
            self._configure_schedule(data)
            self._print_configuration_summary(data)
            if self._ask_yes_no(self._text("setup.confirm_configuration"), True):
                return True
            Console.info(self._text("setup.reconfigure_requested"))
            current_paths = data["backup"]["paths"]

    def _configure_targets(self, data: dict) -> bool:
        print()
        print(self._text("setup.select_targets"))
        print()

        usb = data["targets"]["usb"]
        nas = data["targets"]["nas"]
        use_usb = self._ask_yes_no(self._text("setup.use_usb"), usb["enabled"])
        use_nas = self._ask_yes_no(self._text("setup.use_nas"), nas["enabled"])
        if not use_usb and not use_nas:
            Console.error(self._text("setup.target_required"))
            return self._configure_targets(data)

        usb["enabled"] = use_usb
        if use_usb:
            usb["label"] = self._ask_value(
                self._text("setup.usb_label"), usb["label"]
            )
            usb["repository_path"] = self._ask_value(
                self._text("setup.usb_repository_path"),
                usb["repository_path"],
            )

        nas["enabled"] = use_nas
        if use_nas:
            nas["mount_path"] = self._ask_value(
                self._text("setup.nas_mount_path"), nas["mount_path"]
            )
            nas["repository_path"] = self._ask_value(
                self._text("setup.nas_repository_path"),
                nas["repository_path"],
            )

        if self._selected_targets_available(data):
            return True
        if self._ask_yes_no(self._text("setup.correct_targets"), True):
            return self._configure_targets(data)
        return False

    def _selected_targets_available(self, data: dict) -> bool:
        available = True
        usb = data["targets"]["usb"]
        if usb["enabled"]:
            info = USBTarget(usb["label"]).probe()
            if not info.found:
                Console.error(self._text("setup.usb_unavailable", label=usb["label"]))
                available = False
            elif info.mountpoint is None:
                Console.error(self._text("setup.usb_not_mounted", label=usb["label"]))
                available = False
            elif not info.writable:
                Console.error(self._text("setup.usb_not_writable", path=info.mountpoint))
                available = False

        nas = data["targets"]["nas"]
        if nas["enabled"]:
            path = Path(nas["mount_path"]).expanduser()
            if not path.is_dir():
                Console.error(self._text("setup.nas_unavailable", path=path))
                available = False
            elif not os.access(path, os.W_OK):
                Console.error(self._text("setup.nas_not_writable", path=path))
                available = False
        return available

    def _print_configuration_summary(self, data: dict) -> None:
        title = self._text("setup.summary_title")
        print()
        print(title)
        print("-" * len(title))
        print(self._text("setup.summary_host", value=data["system"]["host_name"]))
        print(self._text("setup.summary_paths"))
        for path in data["backup"]["paths"]:
            print(f"- {path}")
        usb = data["targets"]["usb"]
        nas = data["targets"]["nas"]
        if usb["enabled"]:
            print(self._text("setup.summary_usb", value=usb["label"]))
        if nas["enabled"]:
            print(self._text("setup.summary_nas", value=nas["mount_path"]))
        schedule = data["schedule"]
        value = (
            self._text(
                "setup.summary_schedule_enabled",
                time=schedule["daily_time"],
                days=schedule["interval_days"],
            )
            if schedule["enabled"]
            else self._text("setup.summary_schedule_disabled")
        )
        print(self._text("setup.summary_schedule", value=value))

    def _ask_value(self, label: str, default: str) -> str:
        return input(f"{label} [{default}]: ").strip() or default

    def _configure_schedule(self, data: dict) -> None:
        print()
        enabled = self._ask_yes_no(
            self._text("setup.enable_automatic_backups"),
            data["schedule"]["enabled"],
        )
        data["schedule"]["enabled"] = enabled
        if not enabled:
            return
        data["schedule"]["daily_time"] = self._ask_schedule_time(
            data["schedule"]["daily_time"]
        )
        data["schedule"]["interval_days"] = self._ask_interval_days(
            data["schedule"]["interval_days"]
        )

    def _ask_schedule_time(self, default: str) -> str:
        while True:
            value = input(
                self._text("setup.backup_time", default=default)
            ).strip() or default
            try:
                parsed = datetime.strptime(value, "%H:%M")
            except ValueError:
                Console.error(self._text("setup.invalid_time"))
                continue
            return parsed.strftime("%H:%M")

    def _ask_interval_days(self, default: int) -> int:
        while True:
            value = input(
                self._text("setup.backup_interval", default=default)
            ).strip()
            try:
                interval = int(value) if value else default
            except ValueError:
                interval = 0
            if 1 <= interval <= 365:
                return interval
            Console.error(self._text("setup.invalid_interval"))

    def _check_password(self) -> bool:
        if self.password_file.exists():
            Console.success(self._text("setup.password_present"))
            return True

        Console.error(self._text("setup.password_missing"))
        if not self.interactive:
            Console.warning(self._text("setup.password_creation_skipped"))
            return False
        answer = input(
            self._text(
                "setup.create_password",
                suffix=self._text("common.yes_default_suffix"),
            )
        )
        confirmed = not answer.strip() or is_yes(answer, self._text("common.yes_short"))
        if confirmed and self._create_password_file():
            Console.success(self._text("setup.password_present"))
            return True
        print(self._text("setup.password_not_created"))
        return False

    def _create_password_file(self) -> bool:
        print()
        Console.warning(self._text("setup.password_warning"))
        Console.info(self._text("setup.password_no_reset"))
        Console.info(self._text("setup.password_store_separately"))
        confirmation = input(
            self._text(
                "setup.confirm_data_loss",
                suffix=self._text("common.no_default_suffix"),
            )
        )
        if not is_yes(confirmation, self._text("common.yes_short")):
            Console.warning(self._text("setup.password_not_confirmed"))
            return False

        Console.info(self._text("setup.password_min_length"))
        print()
        while True:
            password = getpass(self._text("setup.new_password"))
            confirmation = getpass(self._text("setup.repeat_password"))
            if not password:
                Console.error(self._text("setup.password_empty"))
            elif len(password) < 8:
                Console.error(self._text("setup.password_too_short"))
            elif password != confirmation:
                Console.error(self._text("setup.password_mismatch"))
            else:
                break
            print()

        self.password_file.parent.mkdir(parents=True, exist_ok=True)
        self.password_file.write_text(password + "\n")
        self.password_file.chmod(0o600)
        Console.success(self._text("setup.password_created"))
        return True

    def _check_program(self, program: str, name: str) -> bool:
        if which(program):
            Console.success(self._text("setup.program_installed", name=name))
            return True
        Console.error(self._text("setup.program_missing", name=name))
        return False

    def _check_programs(self) -> bool:
        return self._check_program("restic", "Restic")

    def _check_repositories(self) -> bool:
        if self.config is None:
            return False

        destinations = RepositoryProvider(self.config).get_all()
        enabled_count = int(self.config.targets.usb.enabled) + int(
            self.config.targets.nas.enabled
        )
        status = len(destinations) == enabled_count
        for destination in destinations:
            status &= self._check_repository(destination)
        return status

    def _check_repository(self, destination: RepositoryDestination) -> bool:
        result = destination.repository.check()
        if result.initialized:
            Console.success(
                self._text("setup.repository_present", target=destination.name)
            )
            return True

        if result.status is RepositoryStatus.WRONG_PASSWORD:
            Console.error(
                self._text("setup.repository_wrong_password", target=destination.name)
            )
            Console.info(result.message)
            Console.info(self._text("setup.repository_password_hint"))
            return False

        if result.status is RepositoryStatus.ERROR:
            Console.error(
                self._text("setup.repository_check_failed", target=destination.name)
            )
            Console.info(result.message)
            return False

        Console.error(self._text("setup.repository_missing", target=destination.name))
        if not self.interactive:
            Console.warning(self._text("setup.repository_creation_skipped"))
            return False
        answer = input(
            self._text(
                "setup.create_repository",
                target=destination.name,
                suffix=self._text("common.yes_default_suffix"),
            )
        )
        if answer.strip() and not is_yes(answer, self._text("common.yes_short")):
            print(self._text("setup.repository_not_created"))
            return False

        created = destination.repository.init_repository()
        if created.initialized:
            Console.success(
                self._text("setup.repository_created", target=destination.name)
            )
            return True
        Console.error(created.message)
        return False

    def _check_scheduler(self) -> bool:
        if self.config is None or not self.config.schedule.enabled:
            return True
        return SystemdScheduler(
            self.config_file,
            self.config.schedule,
            language=self.config.system.language,
        ).install()

    def configure_settings(self) -> bool:
        self._detect_language()
        if not self.config_file.is_file():
            Console.error(self._text("settings.no_config"))
            return False

        try:
            data = yaml.load(
                self.config_file.read_text(encoding="utf-8"),
                Loader=UniqueKeyLoader,
            )
        except (OSError, yaml.YAMLError) as error:
            Console.error(self._text("setup.config_edit_failed", error=error))
            return False

        menu = [
            ("language", self._text("settings.language")),
            ("paths", self._text("settings.backup_paths")),
            ("targets", self._text("settings.targets")),
            ("schedule", self._text("settings.schedule")),
        ]

        while True:
            print()
            title = self._text("settings.title")
            print(title)
            print("=" * len(title))
            print()
            for index, (_, label) in enumerate(menu, start=1):
                print(f"{index}) {label}")
            print(f"{len(menu) + 1}) {self._text('settings.exit')}")
            print()

            raw = input(self._text("settings.prompt")).strip()
            try:
                choice = int(raw)
            except ValueError:
                Console.error(self._text("settings.invalid_choice"))
                continue

            if choice == len(menu) + 1:
                return True
            if choice < 1 or choice > len(menu):
                Console.error(self._text("settings.invalid_choice"))
                continue

            key = menu[choice - 1][0]
            if key == "language":
                self._configure_language(data)
            elif key == "paths":
                data["backup"]["paths"] = self._ask_backup_paths(
                    data["backup"]["paths"]
                )
            elif key == "targets":
                if not self._configure_targets(data):
                    continue
            elif key == "schedule":
                self._configure_schedule(data)

            try:
                AppConfig.model_validate(data)
                backup_file = self.config_file.with_name(f"{self.config_file.name}.bak")
                copy2(self.config_file, backup_file)
                self._write_config(data)
                Console.success(self._text("settings.saved"))
            except (OSError, ValueError, yaml.YAMLError) as error:
                Console.error(self._text("setup.config_save_failed", error=error))

    def run(self) -> bool:
        self._detect_language()
        if self.interactive and not self.config_file.exists():
            self._select_initial_language()
        self._print_header()
        if not self._check_config():
            self._print_summary(False)
            return False
        if not self._load_setup_config():
            self._print_summary(False)
            return False

        password_ok = self._check_password()
        programs_ok = self._check_programs()
        repositories_ok = password_ok and programs_ok and self._check_repositories()
        scheduler_ok = repositories_ok and self._check_scheduler()
        status = password_ok and programs_ok and repositories_ok and scheduler_ok
        self._print_summary(status)
        return status

    def _detect_language(self) -> None:
        if not self.config_file.is_file():
            return
        try:
            config = ConfigLoader(self.config_file).load()
        except ApplicationError:
            return
        self.language = LanguageService(config.system.language)

    def _select_initial_language(self) -> None:
        data = {"system": {"language": LanguageService.default_language}}
        self._configure_language(data, prompt_key="language.initial_selection_prompt")
        self.language_preselected = True

    def _text(self, key: str, **values: object) -> str:
        return self.language.translate(key, **values)
