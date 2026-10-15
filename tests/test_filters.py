from pathlib import Path

import pandas as pd

from filters import filter_programs

DATA_PATH = Path(__file__).parents[1] / "data" / "programs.csv"


def load_programs():
    return pd.read_csv(DATA_PATH)


def test_ielts_filter_excludes_higher_requirement():
    result = filter_programs(load_programs(), 5.5, True, 5_000_000)

    assert result["university"].tolist() == ["University of Aizu"]


def test_standardized_test_filter_excludes_aizu():
    result = filter_programs(load_programs(), 7.0, False, 5_000_000)

    assert "University of Aizu" not in result["university"].tolist()


def test_budget_filter_uses_total_first_year_academic_fees():
    result = filter_programs(load_programs(), 7.0, False, 1_900_000)

    assert result["university"].tolist() == [
        "Yamanashi Gakuin University - iCLA"
    ]

