from importlib.metadata import version

__version__ = version("linux-backup-manager")

dependencies = [
    "PyYAML",
    "pydantic>=2",
]