from pathlib import Path

import pandas as pd

from filters import filter_programs

DATA_PATH = Path(__file__).parents[1] / "data" / "programs.csv"


def load_programs():
    return pd.read_csv(DATA_PATH)


def test_ielts_filter_excludes_higher_requirement():
    result = filter_programs(load_programs(), 5.5, True, 5_000_000, False)

    assert result["university"].tolist() == ["University of Aizu"]


def test_standardized_test_filter_excludes_aizu():
    result = filter_programs(load_programs(), 7.0, False, 5_000_000, False)

    assert "University of Aizu" not in result["university"].tolist()


def test_budget_filter_uses_total_first_year_academic_fees():
    result = filter_programs(load_programs(), 7.0, False, 1_900_000, False)

    assert result["university"].tolist() == [
        "Yamanashi Gakuin University - iCLA"
    ]


def test_maximum_waiver_scenario_reduces_tuition_but_not_other_fees():
    result = filter_programs(load_programs(), 7.0, False, 700_000, True)
    fees_by_university = result.set_index("university")[
        "estimated_first_year_fees_jpy"
    ].to_dict()

    assert fees_by_university == {
        "Yamanashi Gakuin University - iCLA": 200_000,
        "Tokyo International University": 610_000,
    }

