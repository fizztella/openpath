from pathlib import Path

import pandas as pd
import streamlit as st

from filters import evaluate_programs
from shortlist import add_program_keys, build_shortlist, next_deadline, shortlist_csv
from timeline import build_application_timeline, next_timeline_event, timeline_csv

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
selected_countries = st.multiselect(
    "Countries",
    options=sorted(programs["country"].unique()),
    placeholder="All countries",
)
selected_fields = st.multiselect(
    "Fields of study",
    options=sorted(programs["field_category"].unique()),
    placeholder="All fields",
)
ielts_score = st.slider("IELTS overall score", 0.0, 9.0, 6.0, 0.5)
max_first_year_fees = st.number_input(
    "Maximum first-year academic fees (USD)",
    min_value=0,
    max_value=100_000,
    value=20_000,
    step=1_000,
)
use_maximum_tuition_waiver = st.checkbox(
    "Use the maximum published tuition waiver (best-case scenario, not a prediction)"
)
allow_standardized_test = st.checkbox(
    "I can complete an additional standardized academic test"
)

all_evaluated = evaluate_programs(
    programs,
    ielts_score=ielts_score,
    allow_standardized_test=allow_standardized_test,
    max_first_year_fees_usd=max_first_year_fees,
    use_maximum_tuition_waiver=use_maximum_tuition_waiver,
)
evaluated = all_evaluated.copy()
if selected_fields:
    evaluated = evaluated[evaluated["field_category"].isin(selected_fields)]
if selected_countries:
    evaluated = evaluated[evaluated["country"].isin(selected_countries)]

st.subheader("Eligibility results")
if evaluated.empty:
    st.warning("No programs match the selected countries and fields.")
else:
    eligible_count = (evaluated["eligibility_status"] == "Eligible").sum()
    conditional_count = (evaluated["eligibility_status"] == "Conditional").sum()
    not_eligible_count = (evaluated["eligibility_status"] == "Not eligible").sum()

    result_col1, result_col2, result_col3 = st.columns(3)
    result_col1.metric("Eligible", int(eligible_count))
    result_col2.metric("Conditional", int(conditional_count))
    result_col3.metric("Not eligible", int(not_eligible_count))

    selected_statuses = st.multiselect(
        "Result status",
        options=["Eligible", "Conditional", "Not eligible"],
        default=["Eligible", "Conditional", "Not eligible"],
    )
    programs_to_show = evaluated[
        evaluated["eligibility_status"].isin(selected_statuses)
    ].copy()
    status_icons = {
        "Eligible": "🟢 Eligible",
        "Conditional": "🟡 Conditional",
        "Not eligible": "🔴 Not eligible",
    }
    programs_to_show["status_display"] = programs_to_show[
        "eligibility_status"
    ].map(status_icons)

    st.dataframe(
        programs_to_show[
            [
                "status_display",
                "university",
                "program",
                "country",
                "field_category",
                "intake",
                "ielts_overall",
                "standardized_test_required",
                "first_year_academic_fees_usd",
                "native_currency",
                "first_year_academic_fees_native",
                "max_tuition_waiver_percent",
                "estimated_first_year_fees_usd",
                "eligibility_summary",
                "application_deadline_final",
            ]
        ],
        hide_index=True,
        width="stretch",
        column_config={
            "status_display": "Result",
            "university": "University",
            "program": "Program",
            "country": "Country",
            "field_category": "Field",
            "intake": "Intake",
            "ielts_overall": "IELTS",
            "standardized_test_required": "Extra test",
            "first_year_academic_fees_usd": st.column_config.NumberColumn(
                "First-year academic fees (USD)", format="$%d"
            ),
            "native_currency": "Local currency",
            "first_year_academic_fees_native": st.column_config.NumberColumn(
                "Published local fees", format="%.2f"
            ),
            "max_tuition_waiver_percent": "Maximum tuition waiver (%)",
            "estimated_first_year_fees_usd": st.column_config.NumberColumn(
                "Estimated fees in this scenario (USD)", format="$%d"
            ),
            "eligibility_summary": "Why",
            "application_deadline_final": st.column_config.DateColumn("Final deadline"),
        },
    )

    st.subheader("Program details")
    for _, program in programs_to_show.iterrows():
        expander_title = (
            f"{status_icons[program['eligibility_status']]} · "
            f"{program['university']} — {program['program']}"
        )
        with st.expander(expander_title):
            status = program["eligibility_status"]
            if status == "Eligible":
                st.success(program["eligibility_summary"])
            elif status == "Conditional":
                st.warning(program["eligibility_summary"])
            else:
                st.error(program["eligibility_summary"])
            st.caption(program["eligibility_details"])

            details_col, cost_col = st.columns(2)

            with details_col:
                st.markdown(f"**Degree:** {program['degree']}")
                st.markdown(f"**Field:** {program['field_category']}")
                st.markdown(f"**Duration:** {program['duration_years']} years")
                st.markdown(f"**Location:** {program['city']}, {program['country']}")
                st.markdown(f"**Language:** {program['language']}")
                st.markdown(
                    "**Local language required at admission:** "
                    f"{program['local_language_required_at_admission']}"
                )
                st.markdown(f"**Intake:** {program['intake']}")
                ielts_value = (
                    program["ielts_overall"]
                    if pd.notna(program["ielts_overall"])
                    else "No numeric minimum published"
                )
                st.markdown(
                    f"**IELTS ({program['ielts_requirement_type']}):** "
                    f"{ielts_value} — {program['ielts_note']}"
                )
                st.markdown(
                    "**Additional academic test:** "
                    f"{program['standardized_test_required']}"
                )
                st.write(program["accepted_tests"])

            with cost_col:
                if pd.notna(program.get("native_currency")):
                    native_currency = program["native_currency"]
                    native_annual = program["annual_tuition_native"]
                    native_first_year = program["first_year_academic_fees_native"]
                    st.markdown(
                        "**Published annual tuition:** "
                        f"{native_currency} {native_annual:,.2f}"
                    )
                    st.markdown(
                        "**Published first-year academic fees:** "
                        f"{native_currency} {native_first_year:,.2f}"
                    )
                if program.get("native_currency") != "USD":
                    st.markdown(
                        "**Annual tuition (USD comparison):** "
                        f"${int(program['annual_tuition_usd']):,}"
                    )
                    st.markdown(
                        "**First-year academic fees (USD comparison):** "
                        f"${int(program['first_year_academic_fees_usd']):,}"
                    )
                st.markdown(
                    "**Estimated fees in selected scenario:** "
                    f"${int(program['estimated_first_year_fees_usd']):,}"
                )
                waiver = program["max_tuition_waiver_percent"]
                waiver_text = f"{int(waiver)}%" if pd.notna(waiver) else "Not published"
                st.markdown(f"**Maximum published tuition waiver:** {waiver_text}")
                fixed_award = int(program["max_fixed_scholarship_usd"])
                if fixed_award:
                    st.markdown(f"**Maximum fixed scholarship:** ${fixed_award:,}")
                aid_model = program.get("aid_model")
                if pd.notna(aid_model):
                    st.markdown(f"**Aid model:** {aid_model}")
                living_costs = program.get("aid_covers_living_costs")
                if pd.notna(living_costs):
                    st.markdown(f"**Can include living costs:** {living_costs}")
                st.write(program["scholarship_note"])

            st.markdown(f"**Important note:** {program['notes']}")
            st.markdown(
                "**Application window represented:** "
                f"{program['application_open_date']} to "
                f"{program['application_deadline_final']}"
            )
            st.caption(f"Last verified: {program['last_verified']}")
            if pd.notna(program.get("exchange_rate_date")):
                st.caption(
                    "USD comparison rate: "
                    f"1 {program['native_currency']} = "
                    f"{program['usd_per_currency_unit']} USD "
                    f"({program['exchange_rate_date']})"
                )

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

st.divider()
st.subheader("Your shortlist")
keyed_programs = add_program_keys(all_evaluated)
program_labels = keyed_programs.set_index("program_key").apply(
    lambda row: f"{row['university']} — {row['program']} ({row['country']})", axis=1
).to_dict()
selected_program_keys = st.multiselect(
    "Add programs to compare",
    options=keyed_programs["program_key"].tolist(),
    format_func=lambda key: program_labels[key],
    key="shortlist_program_keys",
    placeholder="Choose one or more programs",
)

shortlist = build_shortlist(all_evaluated, selected_program_keys)
if shortlist.empty:
    st.info("Select programs above to build a personal comparison list.")
else:
    upcoming_deadline = next_deadline(shortlist)
    shortlist_col1, shortlist_col2, shortlist_col3 = st.columns(3)
    shortlist_col1.metric("Selected programs", len(shortlist))
    shortlist_col2.metric("Countries", shortlist["country"].nunique())
    shortlist_col3.metric(
        "Next deadline",
        upcoming_deadline.strftime("%Y-%m-%d")
        if upcoming_deadline is not None
        else "No upcoming date",
    )

    shortlist_display = shortlist.copy()
    shortlist_display["status_display"] = shortlist_display[
        "eligibility_status"
    ].map(
        {
            "Eligible": "🟢 Eligible",
            "Conditional": "🟡 Conditional",
            "Not eligible": "🔴 Not eligible",
        }
    )
    st.dataframe(
        shortlist_display[
            [
                "status_display",
                "university",
                "program",
                "country",
                "estimated_first_year_fees_usd",
                "aid_model",
                "aid_covers_living_costs",
                "eligibility_summary",
                "application_deadline_final",
            ]
        ],
        hide_index=True,
        width="stretch",
        column_config={
            "status_display": "Result",
            "university": "University",
            "program": "Program",
            "country": "Country",
            "estimated_first_year_fees_usd": st.column_config.NumberColumn(
                "Estimated first-year fees", format="$%d"
            ),
            "aid_model": "Aid model",
            "aid_covers_living_costs": "Living costs",
            "eligibility_summary": "Remaining issue",
            "application_deadline_final": st.column_config.DateColumn("Deadline"),
        },
    )
    st.download_button(
        "Download shortlist as CSV",
        data=shortlist_csv(shortlist),
        file_name="openpath_shortlist.csv",
        mime="text/csv",
        width="stretch",
    )

    st.subheader("Application timeline")
    st.caption(
        "Official university dates and OpenPath planning milestones are labelled "
        "separately. Planning dates are recommendations, not additional deadlines."
    )
    timeline = build_application_timeline(shortlist)
    upcoming_only = st.checkbox("Show upcoming events only", value=True)
    timeline_to_show = timeline.copy()
    if upcoming_only:
        timeline_to_show = timeline_to_show[timeline_to_show["days_remaining"] >= 0]

    next_event = next_timeline_event(timeline)
    if next_event is not None:
        st.info(
            f"Next action: {next_event['event']} for {next_event['university']} "
            f"on {next_event['event_date']:%Y-%m-%d} ({next_event['timing']})."
        )
    else:
        st.warning("There are no upcoming dated events in the current shortlist.")

    if timeline_to_show.empty:
        st.warning("No timeline events match the current view.")
    else:
        st.dataframe(
            timeline_to_show[
                [
                    "event_date",
                    "timing",
                    "university",
                    "program",
                    "event",
                    "date_type",
                    "note",
                    "source",
                ]
            ],
            hide_index=True,
            width="stretch",
            column_config={
                "event_date": st.column_config.DateColumn("Date"),
                "timing": "Timing",
                "university": "University",
                "program": "Program",
                "event": "Action",
                "date_type": "Date type",
                "note": "Details",
                "source": st.column_config.LinkColumn("Official source"),
            },
        )

    st.download_button(
        "Download application timeline as CSV",
        data=timeline_csv(timeline),
        file_name="openpath_application_timeline.csv",
        mime="text/csv",
        width="stretch",
    )

st.subheader("Sources and limitations")
st.write(
    "OpenPath does not treat missing information as zero and does not predict scholarship "
    "probability without reliable historical decision data."
)

