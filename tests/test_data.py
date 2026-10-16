from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parents[1] / "data" / "programs.csv"


def test_catalog_contains_at_least_forty_programs():
    programs = pd.read_csv(DATA_PATH)

    assert len(programs) >= 40


def test_catalog_has_enough_variety_to_exercise_the_interface():
    programs = pd.read_csv(DATA_PATH)

    assert programs["university"].nunique() >= 21
    assert programs["field_category"].nunique() >= 18


def test_catalog_contains_all_supported_countries_and_currencies():
    programs = pd.read_csv(DATA_PATH)

    assert {"Japan", "Austria", "United States", "Germany", "South Korea"}.issubset(
        set(programs["country"])
    )
    assert {"JPY", "EUR", "USD", "KRW"}.issubset(set(programs["native_currency"]))


def test_program_data_has_required_columns():
    programs = pd.read_csv(DATA_PATH)
    required_columns = {
        "university",
        "program",
        "field_category",
        "duration_years",
        "local_language_required_at_admission",
        "ielts_overall",
        "first_year_academic_fees_usd",
        "application_open_date",
        "application_deadline_final",
        "ielts_requirement_type",
        "scholarship_value_type",
        "max_fixed_scholarship_usd",
        "native_currency",
        "annual_tuition_native",
        "first_year_academic_fees_native",
        "usd_per_currency_unit",
        "exchange_rate_date",
        "admissions_source",
        "last_verified",
    }

    assert required_columns.issubset(programs.columns)


def test_records_keep_native_fees_and_exchange_rate():
    programs = pd.read_csv(DATA_PATH)
    converted = programs[programs["native_currency"].notna()]

    assert not converted.empty
    assert converted["annual_tuition_native"].notna().all()
    assert converted["first_year_academic_fees_native"].notna().all()
    assert converted["usd_per_currency_unit"].gt(0).all()
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


def test_us_block_contains_multiple_financial_aid_models():
    programs = pd.read_csv(DATA_PATH)
    us_programs = programs[programs["country"] == "United States"]

    assert len(us_programs) >= 5
    assert us_programs["aid_model"].nunique() >= 2
    assert (us_programs["native_currency"] == "USD").all()

