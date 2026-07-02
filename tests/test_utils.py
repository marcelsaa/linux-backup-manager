from lbm.utils.prompts import is_yes


def test_is_yes_accepts_y() -> None:
    assert is_yes("y", "y") is True


def test_is_yes_accepts_j() -> None:
    assert is_yes("j", "j") is True


def test_is_yes_accepts_configured_yes_short() -> None:
    assert is_yes("да", "да") is True


def test_is_yes_is_case_insensitive() -> None:
    assert is_yes("Y", "y") is True
    assert is_yes("J", "j") is True


def test_is_yes_strips_whitespace() -> None:
    assert is_yes("  y  ", "y") is True


def test_is_yes_rejects_no() -> None:
    assert is_yes("n", "y") is False


def test_is_yes_rejects_empty() -> None:
    assert is_yes("", "y") is False


def test_is_yes_rejects_unrelated_word() -> None:
    assert is_yes("yes", "y") is False


def test_is_yes_german_j_always_accepted() -> None:
    # "j" is hardcoded so German input works regardless of configured language
    assert is_yes("j", "y") is True


def test_is_yes_english_y_always_accepted() -> None:
    # "y" is hardcoded so English input works regardless of configured language
    assert is_yes("y", "j") is True
