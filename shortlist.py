from datetime import date

import pandas as pd


def program_key(program: pd.Series) -> str:
    """Return a stable identifier for a university-program pair."""
    return f"{program['university']}::{program['program']}"


def add_program_keys(programs: pd.DataFrame) -> pd.DataFrame:
    """Attach stable identifiers used by the shortlist selector."""
    programs = programs.copy()
    programs["program_key"] = programs.apply(program_key, axis=1)
    return programs


def build_shortlist(
    evaluated_programs: pd.DataFrame, selected_program_keys: list[str]
) -> pd.DataFrame:
    """Return selected programs in deadline order."""
    keyed = add_program_keys(evaluated_programs)
    shortlist = keyed[keyed["program_key"].isin(selected_program_keys)].copy()
    shortlist["application_deadline_final"] = pd.to_datetime(
        shortlist["application_deadline_final"], errors="coerce"
    )
    return shortlist.sort_values(
        ["application_deadline_final", "university"], na_position="last"
    )


def next_deadline(shortlist: pd.DataFrame, today: date | None = None):
    """Return the nearest upcoming published deadline, if one exists."""
    if shortlist.empty:
        return None

    today = today or date.today()
    deadlines = pd.to_datetime(
        shortlist["application_deadline_final"], errors="coerce"
    ).dropna()
    upcoming = deadlines[deadlines.dt.date >= today]
    return upcoming.min() if not upcoming.empty else None


def shortlist_csv(shortlist: pd.DataFrame) -> bytes:
    """Export the useful comparison fields without internal identifiers."""
    columns = [
        "university",
        "program",
        "country",
        "eligibility_status",
        "eligibility_summary",
        "intake",
        "ielts_overall",
        "standardized_test_required",
        "estimated_first_year_fees_usd",
        "aid_model",
        "aid_covers_living_costs",
        "application_deadline_final",
        "admissions_source",
        "fees_source",
        "program_source",
        "last_verified",
    ]
    export = shortlist[columns].copy()
    export["application_deadline_final"] = export[
        "application_deadline_final"
    ].dt.strftime("%Y-%m-%d")
    return export.to_csv(index=False).encode("utf-8")
