from datetime import date
from io import BytesIO

import pandas as pd

from timeline import build_application_timeline, next_timeline_event, timeline_xlsx


def sample_shortlist():
    return pd.DataFrame(
        [
            {
                "university": "Example University",
                "program": "Computer Science",
                "country": "Example Country",
                "application_open_date": "2026-09-01",
                "application_deadline_final": "2027-01-31",
                "english_test_required": "Yes",
                "standardized_test_required": "Conditional",
                "accepted_tests": "SAT may be required",
                "scholarship_at_admission": "Yes",
                "admissions_source": "https://example.edu/admissions",
            }
        ]
    )


def test_timeline_separates_official_and_planning_dates():
    timeline = build_application_timeline(sample_shortlist(), date(2026, 10, 15))

    assert set(timeline["date_type"]) == {"Official", "OpenPath plan"}
    assert "Application opens" in timeline["event"].tolist()
    assert "Final application deadline" in timeline["event"].tolist()


def test_timeline_adds_relevant_test_and_scholarship_tasks():
    timeline = build_application_timeline(sample_shortlist(), date(2026, 10, 15))

    assert "Complete English proficiency test" in timeline["event"].tolist()
    assert "Resolve additional academic test requirement" in timeline["event"].tolist()
    assert "Review scholarship requirements" in timeline["event"].tolist()


def test_next_event_skips_past_events():
    timeline = build_application_timeline(sample_shortlist(), date(2026, 10, 15))

    event = next_timeline_event(timeline)

    assert event["event_date"].strftime("%Y-%m-%d") == "2026-11-02"
    assert event["event"] == "Complete English proficiency test"


def test_timeline_excel_includes_date_type_and_source():
    timeline = build_application_timeline(sample_shortlist(), date(2026, 10, 15))

    exported = pd.read_excel(BytesIO(timeline_xlsx(timeline)))

    assert "date_type" in exported.columns
    assert "https://example.edu/admissions" in exported["source"].tolist()
