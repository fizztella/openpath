from datetime import date
from io import BytesIO
from pathlib import Path

import pandas as pd

from filters import evaluate_programs
from shortlist import (
    add_program_keys,
    add_unique_program_key,
    build_shortlist,
    next_deadline,
    shortlist_xlsx,
)

DATA_PATH = Path(__file__).parents[1] / "data" / "programs.csv"


def evaluated_programs():
    programs = pd.read_csv(DATA_PATH)
    return evaluate_programs(programs, 7.0, False, 100_000, False)


def test_shortlist_contains_only_selected_programs():
    evaluated = add_program_keys(evaluated_programs())
    selected = evaluated.iloc[[0, 2]]["program_key"].tolist()

    shortlist = build_shortlist(evaluated, selected)

    assert set(shortlist["program_key"]) == set(selected)


def test_add_unique_program_key_does_not_create_duplicates():
    assert add_unique_program_key(["one"], "two") == ["one", "two"]
    assert add_unique_program_key(["one"], "one") == ["one"]


def test_shortlist_is_sorted_by_deadline():
    evaluated = add_program_keys(evaluated_programs())
    selected = evaluated["program_key"].tolist()

    shortlist = build_shortlist(evaluated, selected)
    published = shortlist["application_deadline_final"].dropna()

    assert published.is_monotonic_increasing


def test_next_deadline_ignores_past_dates():
    shortlist = build_shortlist(
        evaluated_programs(),
        add_program_keys(evaluated_programs())["program_key"].tolist(),
    )

    deadline = next_deadline(shortlist, today=date(2027, 1, 1))

    assert deadline.strftime("%Y-%m-%d") == "2027-01-14"


def test_excel_export_contains_comparison_fields():
    evaluated = add_program_keys(evaluated_programs())
    shortlist = build_shortlist(evaluated, evaluated.iloc[[0]]["program_key"].tolist())

    exported = pd.read_excel(BytesIO(shortlist_xlsx(shortlist)))

    assert "eligibility_status" in exported.columns
    assert "estimated_first_year_fees_usd" in exported.columns
    assert "program_key" not in exported.columns
