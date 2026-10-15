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


def test_new_filter_controls_are_localized():
    for language_code in ("ru", "uk", "es", "de", "ja"):
        assert translate(language_code, "Reset filters") != "Reset filters"
        assert (
            translate(language_code, "Not applicable — OpenPath recommendation")
            != "Not applicable — OpenPath recommendation"
        )


def test_reported_ukrainian_program_notes_are_localized():
    notes = [
        "Standardized academic scores are accepted when applicable to the applicant's education system but are not a universal extra-test requirement",
        "30%, 50%, 65%, 80%, or 100% tuition reduction for the standard study period; renewal is reviewed each semester",
        "Application dates shown are the full published range for the general countries-and-regions schedule",
    ]

    for note in notes:
        assert translate("uk", note) != note
