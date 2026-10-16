from datetime import date
from io import BytesIO

import pandas as pd


def program_key(program: pd.Series) -> str:
    """Return a stable identifier for a university-program pair."""
    return f"{program['university']}::{program['program']}"


def add_program_keys(programs: pd.DataFrame) -> pd.DataFrame:
    """Attach stable identifiers used by the shortlist selector."""
    programs = programs.copy()
    programs["program_key"] = programs.apply(program_key, axis=1)
    return programs


def add_unique_program_key(selected_program_keys: list[str], new_key: str) -> list[str]:
    """Add a program once while preserving the user's comparison order."""
    if new_key in selected_program_keys:
        return list(selected_program_keys)
    return [*selected_program_keys, new_key]


def toggle_program_key(selected_program_keys: list[str], program_key: str) -> list[str]:
    """Toggle comparison membership while preserving the remaining order."""
    if program_key in selected_program_keys:
        return [key for key in selected_program_keys if key != program_key]
    return [*selected_program_keys, program_key]


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


def shortlist_xlsx(shortlist: pd.DataFrame) -> bytes:
    """Export the useful comparison fields as a genuine Excel workbook."""
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
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export.to_excel(writer, sheet_name="Shortlist", index=False)
        worksheet = writer.sheets["Shortlist"]
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions
        for column in worksheet.columns:
            width = min(max(len(str(cell.value or "")) for cell in column) + 2, 48)
            worksheet.column_dimensions[column[0].column_letter].width = width
    return output.getvalue()
