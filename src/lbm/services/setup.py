from pathlib import Path

from lbm.setup.wizard import SetupWizard


class SetupService:
    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file

    def run(self, interactive: bool = True) -> bool:
        return SetupWizard(self.config_file, interactive=interactive).run()
