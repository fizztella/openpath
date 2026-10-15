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
ielts_score = st.slider("IELTS overall score", 0.0, 9.0, 6.0, 0.5)
max_first_year_fees = st.number_input(
    "Maximum first-year academic fees before scholarship (JPY)",
    min_value=0,
    max_value=5_000_000,
    value=2_100_000,
    step=100_000,
)
allow_standardized_test = st.checkbox(
    "Include programs that require an additional standardized academic test"
)

eligible = filter_programs(
    programs,
    ielts_score=ielts_score,
    allow_standardized_test=allow_standardized_test,
    max_first_year_fees_jpy=max_first_year_fees,
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
                "intake",
                "ielts_overall",
                "standardized_test_required",
                "first_year_academic_fees_jpy",
                "max_tuition_waiver_percent",
                "application_deadline",
            ]
        ],
        hide_index=True,
        width="stretch",
        column_config={
            "university": "University",
            "program": "Program",
            "intake": "Intake",
            "ielts_overall": "IELTS",
            "standardized_test_required": "Extra test",
            "first_year_academic_fees_jpy": st.column_config.NumberColumn(
                "First-year academic fees", format="¥%d"
            ),
            "max_tuition_waiver_percent": "Maximum tuition waiver (%)",
            "application_deadline": st.column_config.DateColumn("Final deadline"),
        },
    )

st.subheader("Sources and limitations")
st.write(
    "OpenPath does not treat missing information as zero and does not predict scholarship "
    "probability without reliable historical decision data."
)

