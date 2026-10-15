from pathlib import Path

import pandas as pd

from filters import evaluate_programs, filter_programs

DATA_PATH = Path(__file__).parents[1] / "data" / "programs.csv"


def load_programs():
    return pd.read_csv(DATA_PATH)


def test_ielts_filter_excludes_higher_requirement():
    result = filter_programs(load_programs(), 5.5, True, 100_000, False)

    numeric = result["ielts_requirement_type"].isin(["Minimum", "Target"])
    assert (result.loc[numeric, "ielts_overall"] <= 5.5).all()
    assert "University of Aizu" in result["university"].tolist()


def test_standardized_test_filter_excludes_aizu():
    result = filter_programs(load_programs(), 7.0, False, 100_000, False)

    assert "University of Aizu" not in result["university"].tolist()


def test_budget_filter_uses_total_first_year_academic_fees():
    result = filter_programs(load_programs(), 7.0, False, 12_000, False)

    assert (result["estimated_first_year_fees_usd"] <= 12_000).all()
    assert "Yamanashi Gakuin University - iCLA" in result["university"].tolist()
    assert "Data Science and AI" not in result["program"].tolist()


def test_maximum_waiver_scenario_reduces_tuition_but_not_other_fees():
    result = filter_programs(load_programs(), 7.0, False, 5_000, True)
    fees_by_program = result.set_index("program")[
        "estimated_first_year_fees_usd"
    ].to_dict()

    assert fees_by_program["Data Science"] == 1_260
    assert fees_by_program["Data Science and AI"] == 3_843
    assert fees_by_program["Sustainability and Tourism - Data Science and Information System"] == 1_260


def test_field_filter_returns_only_selected_subjects():
    result = filter_programs(
        load_programs(), 7.0, True, 100_000, False, ["Computer Science"]
    )

    assert not result.empty
    assert (result["field_category"] == "Computer Science").all()


def test_country_filter_returns_only_selected_countries():
    result = filter_programs(
        load_programs(),
        7.0,
        True,
        100_000,
        False,
        selected_countries=["Austria"],
    )

    assert not result.empty
    assert (result["country"] == "Austria").all()


def test_program_without_published_ielts_minimum_is_not_incorrectly_excluded():
    programs = load_programs().iloc[[0]].copy()
    programs["ielts_requirement_type"] = "No published minimum"
    programs["ielts_overall"] = pd.NA

    result = filter_programs(programs, 0.0, True, 100_000, False)

    assert len(result) == 1


def test_fixed_scholarship_is_supported_in_best_case_scenario():
    programs = load_programs().iloc[[0]].copy()
    programs["max_tuition_waiver_percent"] = 0
    programs["max_fixed_scholarship_usd"] = 3_150

    result = filter_programs(programs, 7.0, True, 100_000, True)

    assert result.iloc[0]["estimated_first_year_fees_usd"] == 8_795


def test_conditional_test_program_is_visible_without_test_checkbox():
    result = filter_programs(load_programs(), 7.0, False, 100_000, False)

    assert "Arizona State University" in result["university"].tolist()


def test_evaluation_keeps_failed_programs_and_explains_ielts_gap():
    result = evaluate_programs(load_programs(), 5.5, False, 100_000, False)
    illinois_tech = result[
        result["university"] == "Illinois Institute of Technology"
    ].iloc[0]

    assert illinois_tech["eligibility_status"] == "Not eligible"
    assert "IELTS is 5.5; 6.5 is required" in illinois_tech["eligibility_details"]


def test_evaluation_explains_budget_gap():
    result = evaluate_programs(load_programs(), 7.0, False, 10_000, False)
    temple = result[result["university"] == "Temple University"].iloc[0]

    assert temple["eligibility_status"] == "Not eligible"
    assert "exceed the budget by $32,538" in temple["eligibility_details"]


def test_conditional_test_requirement_produces_conditional_status():
    result = evaluate_programs(load_programs(), 7.0, False, 100_000, False)
    asu = result[result["university"] == "Arizona State University"].iloc[0]

    assert asu["eligibility_status"] == "Conditional"
    assert "may be required conditionally" in asu["eligibility_details"]


def test_required_test_is_blocker_until_applicant_accepts_it():
    without_test = evaluate_programs(load_programs(), 7.0, False, 100_000, False)
    with_test = evaluate_programs(load_programs(), 7.0, True, 100_000, False)

    assert without_test.loc[
        without_test["university"] == "University of Aizu", "eligibility_status"
    ].iloc[0] == "Not eligible"
    assert with_test.loc[
        with_test["university"] == "University of Aizu", "eligibility_status"
    ].iloc[0] == "Conditional"

