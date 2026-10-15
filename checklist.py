import re

import pandas as pd


def build_application_checklist(shortlist: pd.DataFrame) -> pd.DataFrame:
    """Build a compact checklist from requirements already stored in OpenPath."""
    tasks = []
    for _, program in shortlist.iterrows():
        tasks.extend(
            [
                _task(
                    program,
                    "Verify official application instructions",
                    "Required",
                    "Confirm the current intake, deadline, and document list at the official source.",
                ),
                _task(
                    program,
                    "Prepare academic records and required translations",
                    "Core preparation",
                    "Check the institution's rules for transcripts, certificates, translations, and delivery method.",
                ),
            ]
        )

        if program["english_test_required"] == "Yes":
            tasks.append(
                _task(
                    program,
                    "Prepare English proficiency evidence",
                    "Required",
                    str(program["ielts_note"]),
                )
            )

        test_requirement = program["standardized_test_required"]
        if test_requirement in ("Yes", "Conditional"):
            tasks.append(
                _task(
                    program,
                    "Resolve additional academic test requirement",
                    test_requirement,
                    str(program["accepted_tests"]),
                )
            )

        if program["scholarship_at_admission"] == "Yes":
            tasks.append(
                _task(
                    program,
                    "Confirm scholarship application requirements",
                    "Funding",
                    str(program["scholarship_note"]),
                )
            )

        tasks.append(
            _task(
                program,
                "Review and submit the application",
                "Required",
                "Submit before the OpenPath target date and verify that all materials were received.",
            )
        )

    return pd.DataFrame(
        tasks,
        columns=[
            "task_key",
            "program_key",
            "university",
            "program",
            "task",
            "requirement_type",
            "note",
            "source",
        ],
    )


def checklist_progress(checklist: pd.DataFrame, completed_keys: set[str]):
    """Return completed, total, and percentage for a checklist."""
    total = len(checklist)
    completed = checklist["task_key"].isin(completed_keys).sum() if total else 0
    percent = round(completed / total * 100) if total else 0
    return int(completed), total, percent


def _task(program, title, requirement_type, note):
    program_key = program["program_key"]
    task_slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return {
        "task_key": f"{program_key}::{task_slug}",
        "program_key": program_key,
        "university": program["university"],
        "program": program["program"],
        "task": title,
        "requirement_type": requirement_type,
        "note": note,
        "source": program["admissions_source"],
    }
