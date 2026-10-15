# OpenPath

OpenPath helps international applicants compare degree programs using admission requirements, tuition costs, scholarships, and verified official sources.

## Project status

The project is currently in its first development stage. The prototype compares undergraduate programs in Japan, Austria, and the United States using language, field, country, test, and budget filters.

## Planned features

- Filter programs by country, subject, IELTS score, SAT requirement, and budget.
- Compare tuition and estimated first-year costs in USD while preserving each university's published local currency.
- Distinguish merit scholarships, need-based aid, and tuition waivers.
- Classify every result as Eligible, Conditional, or Not eligible and explain why.
- Link every important value to an official source.
- Display when each record was last verified.
- Explain missing or uncertain data instead of inventing values.

## Data methodology

Every record stores separate official sources for admissions, fees, and the academic program, together with the date it was verified. Tuition is kept separate from total first-year academic fees because scholarships often cover only tuition.

See the [data dictionary](docs/data_dictionary.md) for definitions and collection rules.

## Technology

- Python
- pandas
- Streamlit
- Plotly

