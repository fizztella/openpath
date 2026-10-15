# OpenPath data dictionary

This document explains what every field in `data/programs.csv` means.

| Field | Meaning |
| --- | --- |
| `university` | Official English name of the university or college. |
| `program` | Name of the undergraduate program or major. |
| `field_category` | Normalized subject category used for filtering. |
| `country`, `city` | Study location. |
| `degree` | Degree awarded after successful completion. |
| `duration_years` | Standard full-time duration of the degree. |
| `language` | Primary language of instruction. |
| `japanese_required_at_admission` | Whether Japanese proficiency is required when applying. |
| `intake` | Intake represented by this record. Requirements may differ between intakes. |
| `application_open_date` | Opening date of the represented application window. |
| `application_deadline_final` | Final published deadline in ISO format (`YYYY-MM-DD`). |
| `english_test_required` | Whether proof of English proficiency is required. |
| `ielts_requirement_type` | Whether the IELTS value is a minimum, target, absent, or not required. |
| `ielts_overall` | Published overall IELTS requirement or target. |
| `ielts_note` | Important conditions, such as minimum band scores. |
| `standardized_test_required` | Whether a separate academic examination is required. |
| `accepted_tests` | Accepted, optional, or required academic examinations. |
| `annual_tuition_jpy` | Published annual tuition before scholarships. |
| `first_year_academic_fees_jpy` | Tuition and mandatory academic/institutional fees for year one. Housing is excluded. |
| `scholarship_at_admission` | Whether a tuition scholarship can be awarded with admission. |
| `max_tuition_waiver_percent` | Highest published tuition-waiver percentage. Blank means unknown or not applicable. |
| `scholarship_value_type` | Whether aid is percentage-based, fixed, variable, or unavailable. |
| `max_fixed_scholarship_jpy` | Highest fixed scholarship amount in JPY; zero if not applicable. |
| `scholarship_note` | What the scholarship covers and important renewal conditions. |
| `admissions_source` | Official source for entry requirements and deadlines. |
| `fees_source` | Official source for tuition and mandatory fees. |
| `program_source` | Official description of the academic program. |
| `last_verified` | Date on which the record was checked against official sources. |
| `verification_status` | Current verification state of the record. |
| `notes` | Important information that does not fit another field. |

## Data principles

1. Use official university or government sources whenever possible.
2. Never replace a missing value with zero.
3. Record the intake because requirements and fees change over time.
4. Separate tuition from the total first-year cost.
5. Describe what a scholarship actually covers instead of reporting only a percentage.

## Scholarship scenario calculation

The prototype can show a best-case scenario using the maximum published tuition waiver. This is not a prediction of whether an applicant will receive it.

```text
estimated first-year fees
= first-year academic fees
- (annual tuition × maximum waiver percentage)
```

Non-tuition charges remain in the estimate. If the maximum waiver is missing, the program receives no assumed reduction.

