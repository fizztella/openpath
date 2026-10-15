from math import ceil

import pandas as pd


def paginate_results(
    programs: pd.DataFrame, page: int, page_size: int = 6
) -> tuple[pd.DataFrame, int, int]:
    """Return one safe page of results and pagination metadata."""
    if page_size <= 0:
        raise ValueError("page_size must be positive")

    total_pages = max(1, ceil(len(programs) / page_size))
    current_page = min(max(page, 1), total_pages)
    start = (current_page - 1) * page_size
    return programs.iloc[start : start + page_size], current_page, total_pages
