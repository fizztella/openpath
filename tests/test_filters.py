from pathlib import Path

import pandas as pd

from filters import filter_programs

DATA_PATH = Path(__file__).parents[1] / "data" / "programs.csv"


def load_programs():
    return pd.read_csv(DATA_PATH)


def test_ielts_filter_excludes_higher_requirement():
    result = filter_programs(load_programs(), 5.5, True, 5_000_000, False)

    numeric = result["ielts_requirement_type"].isin(["Minimum", "Target"])
    assert (result.loc[numeric, "ielts_overall"] <= 5.5).all()
    assert "University of Aizu" in result["university"].tolist()


def test_standardized_test_filter_excludes_aizu():
    result = filter_programs(load_programs(), 7.0, False, 5_000_000, False)

    assert "University of Aizu" not in result["university"].tolist()


def test_budget_filter_uses_total_first_year_academic_fees():
    result = filter_programs(load_programs(), 7.0, False, 1_900_000, False)

    assert (result["estimated_first_year_fees_jpy"] <= 1_900_000).all()
    assert "Yamanashi Gakuin University - iCLA" in result["university"].tolist()
    assert "Data Science and AI" not in result["program"].tolist()


def test_maximum_waiver_scenario_reduces_tuition_but_not_other_fees():
    result = filter_programs(load_programs(), 7.0, False, 700_000, True)
    fees_by_program = result.set_index("program")[
        "estimated_first_year_fees_jpy"
    ].to_dict()

    assert fees_by_program["Data Science"] == 200_000
    assert fees_by_program["Data Science and AI"] == 610_000
    assert fees_by_program["Sustainability and Tourism - Data Science and Information System"] == 200_000


def test_field_filter_returns_only_selected_subjects():
    result = filter_programs(
        load_programs(), 7.0, True, 5_000_000, False, ["Computer Science"]
    )

    assert not result.empty
    assert (result["field_category"] == "Computer Science").all()


def test_program_without_published_ielts_minimum_is_not_incorrectly_excluded():
    programs = load_programs().iloc[[0]].copy()
    programs["ielts_requirement_type"] = "No published minimum"
    programs["ielts_overall"] = pd.NA

    result = filter_programs(programs, 0.0, True, 5_000_000, False)

    assert len(result) == 1


def test_fixed_scholarship_is_supported_in_best_case_scenario():
    programs = load_programs().iloc[[0]].copy()
    programs["max_tuition_waiver_percent"] = 0
    programs["max_fixed_scholarship_jpy"] = 500_000

    result = filter_programs(programs, 7.0, True, 5_000_000, True)

    assert result.iloc[0]["estimated_first_year_fees_jpy"] == 1_396_000

