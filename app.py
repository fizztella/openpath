from pathlib import Path

import pandas as pd
import streamlit as st

from filters import filter_programs

st.set_page_config(page_title="OpenPath", page_icon="🎓", layout="wide")

st.title("OpenPath")
st.write("Find international degree programs that match your qualifications and budget.")

data_path = Path(__file__).parent / "data" / "programs.csv"
programs = pd.read_csv(data_path)

st.caption(
    "Prototype dataset: every record includes official sources and a verification date. "
    "Requirements can change, so applicants must confirm them before applying."
)

col1, col2, col3 = st.columns(3)
col1.metric("Programs", len(programs))
col2.metric("Universities", programs["university"].nunique())
col3.metric("Countries", programs["country"].nunique())

st.subheader("Your profile")
selected_fields = st.multiselect(
    "Fields of study",
    options=sorted(programs["field_category"].unique()),
    placeholder="All fields",
)
ielts_score = st.slider("IELTS overall score", 0.0, 9.0, 6.0, 0.5)
max_first_year_fees = st.number_input(
    "Maximum first-year academic fees (JPY)",
    min_value=0,
    max_value=5_000_000,
    value=2_100_000,
    step=100_000,
)
use_maximum_tuition_waiver = st.checkbox(
    "Use the maximum published tuition waiver (best-case scenario, not a prediction)"
)
allow_standardized_test = st.checkbox(
    "Include programs that require an additional standardized academic test"
)

eligible = filter_programs(
    programs,
    ielts_score=ielts_score,
    allow_standardized_test=allow_standardized_test,
    max_first_year_fees_jpy=max_first_year_fees,
    use_maximum_tuition_waiver=use_maximum_tuition_waiver,
    selected_fields=selected_fields,
)

st.subheader("Matching programs")
if eligible.empty:
    st.warning("No programs match these filters in the current prototype dataset.")
else:
    st.dataframe(
        eligible[
            [
                "university",
                "program",
                "field_category",
                "intake",
                "ielts_overall",
                "standardized_test_required",
                "first_year_academic_fees_jpy",
                "max_tuition_waiver_percent",
                "estimated_first_year_fees_jpy",
                "application_deadline",
            ]
        ],
        hide_index=True,
        width="stretch",
        column_config={
            "university": "University",
            "program": "Program",
            "field_category": "Field",
            "intake": "Intake",
            "ielts_overall": "IELTS",
            "standardized_test_required": "Extra test",
            "first_year_academic_fees_jpy": st.column_config.NumberColumn(
                "First-year academic fees", format="¥%d"
            ),
            "max_tuition_waiver_percent": "Maximum tuition waiver (%)",
            "estimated_first_year_fees_jpy": st.column_config.NumberColumn(
                "Estimated fees in this scenario", format="¥%d"
            ),
            "application_deadline": st.column_config.DateColumn("Final deadline"),
        },
    )

    st.subheader("Program details")
    for _, program in eligible.iterrows():
        expander_title = f"{program['university']} — {program['program']}"
        with st.expander(expander_title):
            details_col, cost_col = st.columns(2)

            with details_col:
                st.markdown(f"**Degree:** {program['degree']}")
                st.markdown(f"**Field:** {program['field_category']}")
                st.markdown(f"**Duration:** {program['duration_years']} years")
                st.markdown(f"**Location:** {program['city']}, {program['country']}")
                st.markdown(f"**Language:** {program['language']}")
                st.markdown(
                    "**Japanese required at admission:** "
                    f"{program['japanese_required_at_admission']}"
                )
                st.markdown(f"**Intake:** {program['intake']}")
                st.markdown(f"**IELTS:** {program['ielts_overall']} — {program['ielts_note']}")
                st.markdown(
                    "**Additional academic test:** "
                    f"{program['standardized_test_required']}"
                )
                st.write(program["accepted_tests"])

            with cost_col:
                st.markdown(
                    "**Annual tuition:** "
                    f"¥{int(program['annual_tuition_jpy']):,}"
                )
                st.markdown(
                    "**First-year academic fees:** "
                    f"¥{int(program['first_year_academic_fees_jpy']):,}"
                )
                st.markdown(
                    "**Estimated fees in selected scenario:** "
                    f"¥{int(program['estimated_first_year_fees_jpy']):,}"
                )
                waiver = program["max_tuition_waiver_percent"]
                waiver_text = f"{int(waiver)}%" if pd.notna(waiver) else "Not published"
                st.markdown(f"**Maximum published tuition waiver:** {waiver_text}")
                st.write(program["scholarship_note"])

            st.markdown(f"**Important note:** {program['notes']}")
            st.caption(f"Last verified: {program['last_verified']}")

            source_col1, source_col2, source_col3 = st.columns(3)
            source_col1.link_button(
                "Admissions source", program["admissions_source"], width="stretch"
            )
            source_col2.link_button(
                "Fees source", program["fees_source"], width="stretch"
            )
            source_col3.link_button(
                "Program source", program["program_source"], width="stretch"
            )

st.subheader("Sources and limitations")
st.write(
    "OpenPath does not treat missing information as zero and does not predict scholarship "
    "probability without reliable historical decision data."
)

