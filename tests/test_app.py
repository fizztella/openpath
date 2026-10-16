from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).parents[1] / "app.py"


def load_app():
    return AppTest.from_file(APP_PATH, default_timeout=30).run()


def test_shortlist_dropdown_adds_program_and_clears_candidate():
    app = load_app()
    candidate = app.selectbox[1]

    candidate.select(candidate.options[0]).run()
    app.button[-1].click().run()

    assert not app.exception
    assert len(app.session_state["shortlist_program_keys"]) == 1
    assert app.selectbox[1].value is None


def test_result_card_can_add_program_to_comparison():
    app = load_app()
    add_button = next(
        button for button in app.button if button.label == "Add to comparison"
    )

    add_button.click().run()

    assert not app.exception
    assert len(app.session_state["shortlist_program_keys"]) == 1
