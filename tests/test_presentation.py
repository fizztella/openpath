import pandas as pd
import pytest

from presentation import paginate_results


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
