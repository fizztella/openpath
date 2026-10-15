from i18n import LANGUAGES, translate


def test_all_requested_languages_are_available():
    assert set(LANGUAGES.values()) == {"en", "ru", "uk", "es", "de", "ja"}


def test_known_text_is_translated():
    assert translate("ru", "Your profile") == "Ваш профиль"
    assert translate("ja", "Application timeline") == "出願スケジュール"


def test_missing_translation_falls_back_to_english():
    assert translate("de", "Official university name") == "Official university name"


def test_sources_limitation_is_translated_in_every_non_english_language():
    text = (
        "OpenPath does not treat missing information as zero and does not predict "
        "scholarship probability without reliable historical decision data."
    )

    for language_code in ("ru", "uk", "es", "de", "ja"):
        assert translate(language_code, text) != text
