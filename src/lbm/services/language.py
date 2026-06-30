from importlib.resources import files
from typing import Any

import yaml


class LanguageService:
    """Load message catalogs and resolve translated application text."""

    supported_languages = ("de", "en")
    default_language = "de"
    fallback_language = "en"

    def __init__(self, language: str = default_language) -> None:
        self.language = self._normalize(language)
        self._catalogs = {
            code: self._load_catalog(code) for code in self.supported_languages
        }

    def translate(self, key: str, **values: object) -> str:
        for language in self._lookup_order():
            message = self._catalogs.get(language, {}).get(key)
            if message is not None:
                return message.format(**values)
        return key

    def _lookup_order(self) -> tuple[str, ...]:
        order = (
            self.language,
            self.fallback_language,
            self.default_language,
        )
        return tuple(dict.fromkeys(order))

    def _normalize(self, language: str) -> str:
        normalized = language.strip().lower()
        if normalized in self.supported_languages:
            return normalized
        return self.fallback_language

    def _load_catalog(self, language: str) -> dict[str, str]:
        try:
            resource = files("lbm.resources").joinpath("i18n", f"{language}.yaml")
            data = yaml.safe_load(resource.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, yaml.YAMLError):
            return {}
        if not isinstance(data, dict):
            return {}
        return self._flatten(data)

    def _flatten(self, values: dict[str, Any], prefix: str = "") -> dict[str, str]:
        flattened: dict[str, str] = {}
        for name, value in values.items():
            key = f"{prefix}.{name}" if prefix else str(name)
            if isinstance(value, dict):
                flattened.update(self._flatten(value, key))
            elif isinstance(value, str):
                flattened[key] = value
        return flattened
