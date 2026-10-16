import pandas as pd
import pytest

from presentation import paginate_results, search_programs


def test_search_programs_matches_identity_fields_case_insensitively():
    programs = pd.DataFrame(
        {
            "university": ["International Christian University", "WU Vienna"],
            "program": ["College of Liberal Arts", "Business and Economics"],
            "city": ["Mitaka", "Vienna"],
            "country": ["Japan", "Austria"],
        }
    )

    assert search_programs(programs, "christian")["program"].tolist() == [
        "College of Liberal Arts"
    ]
    assert search_programs(programs, "VIENNA")["university"].tolist() == ["WU Vienna"]


def test_search_programs_treats_search_text_as_literal_text():
    programs = pd.DataFrame(
        {
            "university": ["Example [University]"],
            "program": ["Data Science"],
            "city": ["Example City"],
            "country": ["Japan"],
        }
    )

    assert len(search_programs(programs, "[University]")) == 1


def test_pagination_returns_six_results_per_page():
    programs = pd.DataFrame({"program": range(14)})

    page, current_page, total_pages = paginate_results(programs, 2)

    assert page["program"].tolist() == [6, 7, 8, 9, 10, 11]
    assert current_page == 2
    assert total_pages == 3


def test_pagination_clamps_invalid_page_number():
    programs = pd.DataFrame({"program": range(7)})

    page, current_page, total_pages = paginate_results(programs, 99)

    assert page["program"].tolist() == [6]
    assert current_page == 2
    assert total_pages == 2


def test_pagination_handles_empty_results():
    page, current_page, total_pages = paginate_results(pd.DataFrame(), 1)

    assert page.empty
    assert current_page == 1
    assert total_pages == 1


def test_pagination_rejects_invalid_page_size():
    with pytest.raises(ValueError):
        paginate_results(pd.DataFrame(), 1, 0)


def test_pagination_handles_a_large_result_set():
    programs = pd.DataFrame({"program": range(1_000)})

    page, current_page, total_pages = paginate_results(programs, 167)

    assert len(page) == 4
    assert current_page == 167
    assert total_pages == 167
