import pandas as pd


def filter_programs(
    programs: pd.DataFrame,
    ielts_score: float,
    allow_standardized_test: bool,
    max_first_year_fees_jpy: int,
) -> pd.DataFrame:
    """Return programs that match the applicant's current profile."""
    eligible = programs[
        (programs["ielts_overall"] <= ielts_score)
        & (programs["first_year_academic_fees_jpy"] <= max_first_year_fees_jpy)
    ].copy()

    if not allow_standardized_test:
        eligible = eligible[eligible["standardized_test_required"] == "No"]

    return eligible

