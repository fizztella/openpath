from i18n import LANGUAGES, translate


def test_all_requested_languages_are_available():
    assert set(LANGUAGES.values()) == {"en", "ru", "uk", "es", "de", "ja"}


def test_known_text_is_translated():
    assert translate("ru", "Your profile") == "Ваш профиль"
    assert translate("ja", "Application timeline") == "出願スケジュール"


def test_missing_translation_falls_back_to_english():
    assert translate("de", "Official university name") == "Official university name"
