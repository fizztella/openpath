from datetime import date
from io import BytesIO

import pandas as pd


def build_application_timeline(
    shortlist: pd.DataFrame, today: date | None = None
) -> pd.DataFrame:
    """Build official dates and clearly labelled planning milestones."""
    today = today or date.today()
    events = []

    for _, program in shortlist.iterrows():
        deadline = pd.to_datetime(
            program["application_deadline_final"], errors="coerce"
        )
        opening = pd.to_datetime(program["application_open_date"], errors="coerce")

        if pd.notna(opening):
            events.append(
                _event(
                    program,
                    opening,
                    "Application opens",
                    "Official",
                    "Published application opening date",
                )
            )

        if pd.isna(deadline):
            continue

        events.append(
            _event(
                program,
                deadline - pd.Timedelta(days=120),
                "Start preparing documents",
                "OpenPath plan",
                "Recommended planning date, not a university deadline",
            )
        )

        if program["english_test_required"] == "Yes":
            events.append(
                _event(
                    program,
                    deadline - pd.Timedelta(days=90),
                    "Complete English proficiency test",
                    "OpenPath plan",
                    "Leaves time for results and a possible retake",
                )
            )

        if program["standardized_test_required"] in ("Yes", "Conditional"):
            events.append(
                _event(
                    program,
                    deadline - pd.Timedelta(days=90),
                    "Resolve additional academic test requirement",
                    "OpenPath plan",
                    str(program["accepted_tests"]),
                )
            )

        if program["scholarship_at_admission"] == "Yes":
            events.append(
                _event(
                    program,
                    deadline - pd.Timedelta(days=75),
                    "Review scholarship requirements",
                    "OpenPath plan",
                    "Check whether aid needs separate forms, essays, or earlier submission",
                )
            )

        events.append(
            _event(
                program,
                deadline - pd.Timedelta(days=14),
                "Target application submission",
                "OpenPath plan",
                "Recommended buffer before the official deadline",
            )
        )
        events.append(
            _event(
                program,
                deadline,
                "Final application deadline",
                "Official",
                "Published final deadline for the represented intake",
            )
        )

    columns = [
        "event_date",
        "university",
        "program",
        "country",
        "event",
        "date_type",
        "note",
        "source",
    ]
    timeline = pd.DataFrame(events, columns=columns)
    if timeline.empty:
        return timeline.assign(days_remaining=pd.Series(dtype="int64"), timing="")

    timeline["event_date"] = pd.to_datetime(timeline["event_date"])
    timeline["days_remaining"] = timeline["event_date"].dt.date.map(
        lambda event_date: (event_date - today).days
    )
    timeline["timing"] = timeline["days_remaining"].map(_timing_label)
    return timeline.sort_values(["event_date", "university", "event"]).reset_index(
        drop=True
    )


def _event(program, event_date, title, date_type, note):
    return {
        "event_date": event_date,
        "university": program["university"],
        "program": program["program"],
        "country": program["country"],
        "event": title,
        "date_type": date_type,
        "note": note,
        "source": program["admissions_source"] if date_type == "Official" else "",
    }


def _timing_label(days_remaining: int) -> str:
    if days_remaining < 0:
        return f"Past by {abs(days_remaining)} days"
    if days_remaining == 0:
        return "Today"
    if days_remaining <= 30:
        return f"Due in {days_remaining} days"
    return f"In {days_remaining} days"


def next_timeline_event(timeline: pd.DataFrame):
    """Return the nearest event that has not passed."""
    if timeline.empty:
        return None
    upcoming = timeline[timeline["days_remaining"] >= 0]
    return upcoming.iloc[0] if not upcoming.empty else None


def timeline_xlsx(timeline: pd.DataFrame) -> bytes:
    """Export timeline dates and source links as a genuine Excel workbook."""
    export = timeline.copy()
    export["event_date"] = export["event_date"].dt.strftime("%Y-%m-%d")
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export.to_excel(writer, sheet_name="Timeline", index=False)
        worksheet = writer.sheets["Timeline"]
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions
        for column in worksheet.columns:
            width = min(max(len(str(cell.value or "")) for cell in column) + 2, 48)
            worksheet.column_dimensions[column[0].column_letter].width = width
    return output.getvalue()
