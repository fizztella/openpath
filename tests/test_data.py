from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parents[1] / "data" / "programs.csv"


def test_prototype_contains_at_least_ten_programs():
    programs = pd.read_csv(DATA_PATH)

    assert len(programs) >= 10


def test_program_data_has_required_columns():
    programs = pd.read_csv(DATA_PATH)
    required_columns = {
        "university",
        "program",
        "field_category",
        "duration_years",
        "japanese_required_at_admission",
        "ielts_overall",
        "first_year_academic_fees_jpy",
        "application_open_date",
        "application_deadline_final",
        "ielts_requirement_type",
        "scholarship_value_type",
        "max_fixed_scholarship_jpy",
        "native_currency",
        "annual_tuition_native",
        "first_year_academic_fees_native",
        "jpy_per_currency_unit",
        "exchange_rate_date",
        "admissions_source",
        "last_verified",
    }

    assert required_columns.issubset(programs.columns)


def test_non_jpy_records_keep_native_fees_and_exchange_rate():
    programs = pd.read_csv(DATA_PATH)
    converted = programs[programs["native_currency"].notna()]

    assert not converted.empty
    assert converted["annual_tuition_native"].notna().all()
    assert converted["first_year_academic_fees_native"].notna().all()
    assert converted["jpy_per_currency_unit"].gt(0).all()
    assert converted["exchange_rate_date"].notna().all()


def test_official_sources_are_https_urls():
    programs = pd.read_csv(DATA_PATH)

    for source_column in ("admissions_source", "fees_source", "program_source"):
        assert programs[source_column].str.startswith("https://").all()


def test_verified_records_have_verification_dates():
    programs = pd.read_csv(DATA_PATH)
    verified = programs[programs["verification_status"] == "Verified"]

    assert verified["last_verified"].notna().all()


def test_numeric_ielts_requirements_have_scores():
    programs = pd.read_csv(DATA_PATH)
    numeric_requirements = programs["ielts_requirement_type"].isin(
        ["Minimum", "Target"]
    )

    assert programs.loc[numeric_requirements, "ielts_overall"].notna().all()

