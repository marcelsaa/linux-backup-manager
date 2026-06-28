from string import Formatter
from unittest.mock import patch

from lbm.services.language import LanguageService


def test_language_service_loads_german_and_english_catalogs() -> None:
    german = LanguageService("de")
    english = LanguageService("en")

    assert german.translate("language.selected", language="de") == (
        "Sprache ausgewählt: de"
    )
    assert english.translate("language.selected", language="en") == (
        "Language selected: en"
    )


def test_unknown_language_falls_back_to_english() -> None:
    language = LanguageService("fr")

    assert language.language == "en"
    assert language.translate("language.invalid") == "Please enter 'de' or 'en'."


def test_missing_message_falls_back_to_the_other_catalog() -> None:
    catalogs = {
        "de": {"only.german": "Nur Deutsch"},
        "en": {"only.english": "English only"},
    }

    with patch.object(
        LanguageService,
        "_load_catalog",
        side_effect=lambda language: catalogs[language],
    ):
        german = LanguageService("de")
        english = LanguageService("en")

    assert german.translate("only.english") == "English only"
    assert english.translate("only.german") == "Nur Deutsch"


def test_missing_message_returns_stable_key() -> None:
    assert LanguageService("de").translate("not.translated.yet") == "not.translated.yet"


def test_german_and_english_catalogs_have_matching_keys_and_placeholders() -> None:
    language = LanguageService()
    german = language._catalogs["de"]
    english = language._catalogs["en"]

    assert german.keys() == english.keys()
    for key in german:
        german_fields = {name for _, name, _, _ in Formatter().parse(german[key]) if name}
        english_fields = {name for _, name, _, _ in Formatter().parse(english[key]) if name}
        assert german_fields == english_fields, key
