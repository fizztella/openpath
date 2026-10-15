import pandas as pd

from checklist import build_application_checklist, checklist_progress


def sample_shortlist(test_requirement="Conditional", scholarship="Yes"):
    return pd.DataFrame(
        [
            {
                "program_key": "Example University::Computer Science",
                "university": "Example University",
                "program": "Computer Science",
                "english_test_required": "Yes",
                "ielts_note": "IELTS 6.5",
                "standardized_test_required": test_requirement,
                "accepted_tests": "SAT may be required",
                "scholarship_at_admission": scholarship,
                "scholarship_note": "Separate funding form may be required",
                "admissions_source": "https://example.edu/admissions",
            }
        ]
    )


def test_checklist_uses_only_relevant_conditional_tasks():
    checklist = build_application_checklist(sample_shortlist())

    assert "Prepare English proficiency evidence" in checklist["task"].tolist()
    assert "Resolve additional academic test requirement" in checklist["task"].tolist()
    assert "Confirm scholarship application requirements" in checklist["task"].tolist()


def test_checklist_omits_unneeded_test_and_funding_tasks():
    checklist = build_application_checklist(sample_shortlist("No", "No"))

    assert "Resolve additional academic test requirement" not in checklist["task"].tolist()
    assert "Confirm scholarship application requirements" not in checklist["task"].tolist()


def test_checklist_task_keys_are_unique():
    checklist = build_application_checklist(sample_shortlist())

    assert checklist["task_key"].is_unique


def test_checklist_progress_counts_completed_tasks():
    checklist = build_application_checklist(sample_shortlist())
    completed_keys = set(checklist.iloc[:2]["task_key"])

    completed, total, percent = checklist_progress(checklist, completed_keys)

    assert completed == 2
    assert total == len(checklist)
    assert percent == round(2 / len(checklist) * 100)
