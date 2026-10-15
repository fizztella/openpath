import pandas as pd


def evaluate_programs(
    programs: pd.DataFrame,
    ielts_score: float,
    allow_standardized_test: bool,
    max_first_year_fees_usd: int,
    use_maximum_tuition_waiver: bool,
    selected_fields: list[str] | None = None,
    selected_countries: list[str] | None = None,
) -> pd.DataFrame:
    """Evaluate programs and explain their fit without hiding failed matches."""
    programs = programs.copy()

    if selected_fields:
        programs = programs[programs["field_category"].isin(selected_fields)].copy()

    if selected_countries:
        programs = programs[programs["country"].isin(selected_countries)].copy()

    waiver_percent = programs["max_tuition_waiver_percent"].fillna(0)
    fixed_scholarship = programs["max_fixed_scholarship_usd"].fillna(0)

    if use_maximum_tuition_waiver:
        percentage_reduction = programs["annual_tuition_usd"] * waiver_percent / 100
        tuition_reduction = pd.concat(
            [percentage_reduction, fixed_scholarship], axis=1
        ).max(axis=1)
    else:
        tuition_reduction = 0

    programs["estimated_first_year_fees_usd"] = (
        programs["first_year_academic_fees_usd"] - tuition_reduction
    ).clip(lower=0).round().astype(int)

    evaluations = programs.apply(
        _evaluate_program,
        axis=1,
        ielts_score=ielts_score,
        allow_standardized_test=allow_standardized_test,
        max_first_year_fees_usd=max_first_year_fees_usd,
    )
    programs[["eligibility_status", "eligibility_summary", "eligibility_details"]] = (
        pd.DataFrame(evaluations.tolist(), index=programs.index)
    )

    status_order = {"Eligible": 0, "Conditional": 1, "Not eligible": 2}
    programs["_status_order"] = programs["eligibility_status"].map(status_order)
    return programs.sort_values(
        ["_status_order", "estimated_first_year_fees_usd", "university"]
    ).drop(columns="_status_order")


def _evaluate_program(
    program: pd.Series,
    ielts_score: float,
    allow_standardized_test: bool,
    max_first_year_fees_usd: int,
) -> tuple[str, str, str]:
    blockers = []
    conditions = []
    matches = []

    if program["ielts_requirement_type"] in ("Minimum", "Target"):
        required_ielts = float(program["ielts_overall"])
        if ielts_score < required_ielts:
            blockers.append(
                f"IELTS is {ielts_score:.1f}; {required_ielts:.1f} is required"
            )
        else:
            matches.append(f"IELTS requirement met ({required_ielts:.1f})")
    else:
        matches.append("No numeric IELTS minimum is published")

    estimated_fees = int(program["estimated_first_year_fees_usd"])
    if estimated_fees > max_first_year_fees_usd:
        difference = estimated_fees - max_first_year_fees_usd
        blockers.append(f"First-year academic fees exceed the budget by ${difference:,}")
    else:
        remaining = max_first_year_fees_usd - estimated_fees
        matches.append(f"Within the academic-fee budget by ${remaining:,}")

    test_requirement = program["standardized_test_required"]
    if test_requirement == "Yes":
        if allow_standardized_test:
            conditions.append("A separate academic test must still be completed")
        else:
            blockers.append("A required additional academic test is not in the profile")
    elif test_requirement == "Conditional":
        conditions.append("An additional academic test may be required conditionally")
    else:
        matches.append("No additional academic test is universally required")

    if blockers:
        status = "Not eligible"
        summary = blockers[0]
    elif conditions:
        status = "Conditional"
        summary = conditions[0]
    else:
        status = "Eligible"
        summary = "Current profile meets the represented requirements"

    details = "; ".join(blockers + conditions + matches)
    return status, summary, details


def filter_programs(
    programs: pd.DataFrame,
    ielts_score: float,
    allow_standardized_test: bool,
    max_first_year_fees_usd: int,
    use_maximum_tuition_waiver: bool,
    selected_fields: list[str] | None = None,
    selected_countries: list[str] | None = None,
) -> pd.DataFrame:
    """Return programs that match the applicant's current profile."""
    evaluated = evaluate_programs(
        programs,
        ielts_score=ielts_score,
        allow_standardized_test=allow_standardized_test,
        max_first_year_fees_usd=max_first_year_fees_usd,
        use_maximum_tuition_waiver=use_maximum_tuition_waiver,
        selected_fields=selected_fields,
        selected_countries=selected_countries,
    )
    return evaluated[evaluated["eligibility_status"] != "Not eligible"].copy()

