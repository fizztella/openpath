import pandas as pd


def filter_programs(
    programs: pd.DataFrame,
    ielts_score: float,
    allow_standardized_test: bool,
    max_first_year_fees_jpy: int,
    use_maximum_tuition_waiver: bool,
    selected_fields: list[str] | None = None,
    selected_countries: list[str] | None = None,
) -> pd.DataFrame:
    """Return programs that match the applicant's current profile."""
    programs = programs.copy()
    waiver_percent = programs["max_tuition_waiver_percent"].fillna(0)
    fixed_scholarship = programs["max_fixed_scholarship_jpy"].fillna(0)

    if use_maximum_tuition_waiver:
        percentage_reduction = programs["annual_tuition_jpy"] * waiver_percent / 100
        tuition_reduction = pd.concat(
            [percentage_reduction, fixed_scholarship], axis=1
        ).max(axis=1)
    else:
        tuition_reduction = 0

    programs["estimated_first_year_fees_jpy"] = (
        programs["first_year_academic_fees_jpy"] - tuition_reduction
    ).round().astype(int)

    numeric_ielts_requirement = programs["ielts_requirement_type"].isin(
        ["Minimum", "Target"]
    )
    passes_ielts = (~numeric_ielts_requirement) | (
        programs["ielts_overall"] <= ielts_score
    )

    eligible = programs[
        passes_ielts
        & (programs["estimated_first_year_fees_jpy"] <= max_first_year_fees_jpy)
    ].copy()

    if not allow_standardized_test:
        eligible = eligible[eligible["standardized_test_required"] == "No"]

    if selected_fields:
        eligible = eligible[eligible["field_category"].isin(selected_fields)]

    if selected_countries:
        eligible = eligible[eligible["country"].isin(selected_countries)]

    return eligible

