from pathlib import Path

import pandas as pd
import streamlit as st

from checklist import build_application_checklist, checklist_progress
from filters import evaluate_programs
from i18n import LANGUAGES, translate
from presentation import paginate_results
from shortlist import add_program_keys, build_shortlist, next_deadline, shortlist_xlsx
from timeline import build_application_timeline, next_timeline_event, timeline_xlsx

st.set_page_config(page_title="OpenPath", page_icon="🎓", layout="wide")

styles_path = Path(__file__).parent / "styles.css"
st.markdown(f"<style>{styles_path.read_text()}</style>", unsafe_allow_html=True)

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

theme = {
    "dark": {
        "bg": "#0b0f14",
        "panel": "#141a22",
        "panel_strong": "#19212b",
        "text": "#edf2f7",
        "muted": "#9aa7b5",
        "border": "rgba(255, 255, 255, 0.10)",
        "header": "rgba(11, 15, 20, 0.94)",
    },
    "light": {
        "bg": "#f5f7fa",
        "panel": "#ffffff",
        "panel_strong": "#eef2f7",
        "text": "#17202b",
        "muted": "#5f6b78",
        "border": "rgba(23, 32, 43, 0.13)",
        "header": "rgba(245, 247, 250, 0.94)",
    },
}[st.session_state.theme_mode]
st.markdown(
    f"""
    <style>
    :root, .stApp {{
        --op-bg: {theme["bg"]};
        --op-panel: {theme["panel"]};
        --op-panel-strong: {theme["panel_strong"]};
        --op-text: {theme["text"]};
        --op-muted: {theme["muted"]};
        --op-border: {theme["border"]};
        --background-color: {theme["bg"]};
        --secondary-background-color: {theme["panel"]};
        --text-color: {theme["text"]};
        --primary-color: #3976c3;
    }}
    [data-testid="stHeader"] {{ background: {theme["header"]}; }}
    [data-testid="stDialog"],
    [data-testid="stDialog"] p,
    [data-testid="stDialog"] span,
    [data-testid="stDialog"] strong,
    [data-testid="stDialog"] label,
    [data-testid="stDialog"] h1,
    [data-testid="stDialog"] h2,
    [data-testid="stDialog"] h3 {{
        color: {theme["text"]} !important;
    }}
    [data-testid="stDialog"] [data-testid="stCaptionContainer"] {{
        color: {theme["muted"]} !important;
    }}
    [data-baseweb="popover"],
    [role="listbox"],
    [role="option"] {{
        background-color: {theme["panel"]} !important;
        color: {theme["text"]} !important;
    }}
    [role="option"]:hover {{
        background-color: {theme["panel_strong"]} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

hero_col, language_col, theme_col = st.columns([4, 1.15, 0.3])
with language_col:
    current_language = st.session_state.get("interface_language", "English")
    language_name = st.selectbox(
        translate(LANGUAGES.get(current_language, "en"), "Interface language"),
        options=list(LANGUAGES),
        index=0,
        key="interface_language",
    )
language_code = LANGUAGES[language_name]


def t(text):
    return translate(language_code, text)


def toggle_theme():
    st.session_state.theme_mode = (
        "light" if st.session_state.theme_mode == "dark" else "dark"
    )


with theme_col:
    st.markdown("<div class='op-theme-label'>&nbsp;</div>", unsafe_allow_html=True)
    st.button(
        "☀️" if st.session_state.theme_mode == "dark" else "🌙",
        help=t("Switch to light theme")
        if st.session_state.theme_mode == "dark"
        else t("Switch to dark theme"),
        on_click=toggle_theme,
        key="theme_toggle",
        width="stretch",
    )


def timing_text(days):
    if days < 0:
        return t("Past by {days} days").format(days=abs(days))
    if days == 0:
        return t("Today")
    key = "Due in {days} days" if days <= 30 else "In {days} days"
    return t(key).format(days=days)


def render_program_details(program):
    status = program["eligibility_status"]
    message = t(str(program["eligibility_summary"]))
    if status == "Eligible":
        st.success(message)
    elif status == "Conditional":
        st.warning(message)
    else:
        st.error(message)

    details_col, cost_col = st.columns(2)
    with details_col:
        st.markdown(f"**{t('Degree')}:** {t(str(program['degree']))}")
        st.markdown(f"**{t('Field')}:** {t(str(program['field_category']))}")
        st.markdown(f"**{t('Duration')}:** {program['duration_years']} {t('years')}")
        st.markdown(
            f"**{t('Location')}:** {program['city']}, {t(str(program['country']))}"
        )
        st.markdown(f"**{t('Language')}:** {t(str(program['language']))}")
        st.markdown(
            f"**{t('Local language required at admission')}:** {t(str(program['local_language_required_at_admission']))}"
        )
        st.markdown(f"**{t('Intake')}:** {program['intake']}")
        ielts_value = (
            program["ielts_overall"]
            if pd.notna(program["ielts_overall"])
            else t("Not published")
        )
        st.markdown(f"**IELTS:** {ielts_value} — {program['ielts_note']}")
        st.markdown(
            f"**{t('Additional academic test')}:** {t(str(program['standardized_test_required']))}"
        )
        st.caption(str(program["accepted_tests"]))
    with cost_col:
        if pd.notna(program.get("native_currency")):
            currency = program["native_currency"]
            st.markdown(
                f"**{t('Published annual tuition')}:** {currency} {program['annual_tuition_native']:,.2f}"
            )
            st.markdown(
                f"**{t('Published first-year academic fees')}:** {currency} {program['first_year_academic_fees_native']:,.2f}"
            )
        if program.get("native_currency") != "USD":
            st.markdown(
                f"**{t('Annual tuition (USD comparison)')}:** ${int(program['annual_tuition_usd']):,}"
            )
            st.markdown(
                f"**{t('First-year academic fees (USD comparison)')}:** ${int(program['first_year_academic_fees_usd']):,}"
            )
        st.markdown(
            f"**{t('Estimated fees in selected scenario')}:** ${int(program['estimated_first_year_fees_usd']):,}"
        )
        waiver = program["max_tuition_waiver_percent"]
        waiver_text = f"{int(waiver)}%" if pd.notna(waiver) else t("Not published")
        st.markdown(f"**{t('Maximum published tuition waiver')}:** {waiver_text}")
        fixed_award = int(program["max_fixed_scholarship_usd"])
        if fixed_award:
            st.markdown(f"**{t('Maximum fixed scholarship')}:** ${fixed_award:,}")
        if pd.notna(program.get("aid_model")):
            st.markdown(f"**{t('Aid model')}:** {t(str(program['aid_model']))}")
        st.markdown(
            f"**{t('Can include living costs')}:** {t(str(program['aid_covers_living_costs']))}"
        )
        st.caption(str(program["scholarship_note"]))
    st.markdown(f"**{t('Important note')}:** {program['notes']}")
    st.markdown(
        f"**{t('Application window represented')}:** {program['application_open_date']} — {program['application_deadline_final']}"
    )
    st.caption(f"{t('Last verified')}: {program['last_verified']}")
    source_col1, source_col2, source_col3 = st.columns(3)
    source_col1.link_button(
        t("Admissions source"), program["admissions_source"], width="stretch"
    )
    source_col2.link_button(t("Fees source"), program["fees_source"], width="stretch")
    source_col3.link_button(
        t("Program source"), program["program_source"], width="stretch"
    )


@st.dialog(t("Program details"), width="large")
def show_program_dialog(program):
    st.markdown(f"## {program['university']}")
    st.markdown(f"### {program['program']}")
    summary_col, deadline_col = st.columns(2)
    summary_col.metric(
        t("Estimated fees"),
        f"${int(program['estimated_first_year_fees_usd']):,}",
    )
    deadline = program["application_deadline_final"]
    deadline_col.metric(
        t("Deadline"), str(deadline) if pd.notna(deadline) else t("Not published")
    )
    render_program_details(program)


with hero_col:
    st.markdown(
        f"""
        <section class="op-hero">
            <div class="op-eyebrow">{t("Verified admissions intelligence")}</div>
            <h1 class="op-title">Open<span>Path</span></h1>
            <p class="op-subtitle">
                {t("Find international degree programs that match your qualifications and budget.")}
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

data_path = Path(__file__).parent / "data" / "programs.csv"
programs = pd.read_csv(data_path)

st.caption(
    t(
        "Prototype dataset: every record includes official sources and a verification date. Requirements can change, so applicants must confirm them before applying."
    )
)

col1, col2, col3 = st.columns(3)
col1.metric(t("Programs"), len(programs))
col2.metric(t("Universities"), programs["university"].nunique())
col3.metric(t("Countries"), programs["country"].nunique())

program_search_tab, shortlist_tab = st.tabs(
    [f"🔎 {t('Program search')}", f"⭐ {t('Shortlist & timeline')}"]
)

with program_search_tab:
    st.subheader(t("Your profile"))
    selected_countries = st.multiselect(
        t("Countries"),
        options=sorted(programs["country"].unique()),
        format_func=t,
        placeholder=t("All countries"),
    )
    selected_fields = st.multiselect(
        t("Fields of study"),
        options=sorted(programs["field_category"].unique()),
        format_func=t,
        placeholder=t("All fields"),
    )
    ielts_score = st.slider(t("IELTS overall score"), 0.0, 9.0, 6.0, 0.5)
    max_first_year_fees = st.number_input(
        t("Maximum first-year academic fees (USD)"),
        min_value=0,
        max_value=100_000,
        value=20_000,
        step=1_000,
    )
    use_maximum_tuition_waiver = st.checkbox(
        t(
            "Use the maximum published tuition waiver (best-case scenario, not a prediction)"
        )
    )
    allow_standardized_test = st.checkbox(
        t("I can complete an additional standardized academic test")
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

    st.subheader(t("Eligibility results"))
    if evaluated.empty:
        st.warning(t("No programs match the selected countries and fields."))
    else:
        eligible_count = (evaluated["eligibility_status"] == "Eligible").sum()
        conditional_count = (evaluated["eligibility_status"] == "Conditional").sum()
        not_eligible_count = (evaluated["eligibility_status"] == "Not eligible").sum()

        result_col1, result_col2, result_col3 = st.columns(3)
        result_col1.metric(t("Eligible"), int(eligible_count))
        result_col2.metric(t("Conditional"), int(conditional_count))
        result_col3.metric(t("Not eligible"), int(not_eligible_count))

        selected_statuses = st.multiselect(
            t("Result status"),
            options=["Eligible", "Conditional", "Not eligible"],
            default=["Eligible", "Conditional", "Not eligible"],
            format_func=t,
        )
        programs_to_show = evaluated[
            evaluated["eligibility_status"].isin(selected_statuses)
        ].copy()
        status_icons = {
            "Eligible": f"🟢 {t('Eligible')}",
            "Conditional": f"🟡 {t('Conditional')}",
            "Not eligible": f"🔴 {t('Not eligible')}",
        }
        programs_to_show["status_display"] = programs_to_show["eligibility_status"].map(
            status_icons
        )
        programs_to_show["country_display"] = programs_to_show["country"].map(t)
        programs_to_show["aid_model_display"] = programs_to_show["aid_model"].map(t)

        view_mode = st.radio(
            t("Results view"),
            options=["Cards", "Compact table"],
            format_func=t,
            horizontal=True,
        )
        if view_mode == "Cards":
            _, _, total_pages = paginate_results(programs_to_show, 1)
            page_key = "results_page"
            st.session_state[page_key] = min(
                max(st.session_state.get(page_key, 1), 1), total_pages
            )
            previous_col, page_col, next_col = st.columns([1, 2, 1])
            if previous_col.button(
                t("Previous"), disabled=st.session_state[page_key] == 1, width="stretch"
            ):
                st.session_state[page_key] -= 1
                st.rerun()
            page_col.markdown(
                f"<div class='op-page-count'>{st.session_state[page_key]} / {total_pages}</div>",
                unsafe_allow_html=True,
            )
            if next_col.button(
                t("Next"),
                disabled=st.session_state[page_key] == total_pages,
                width="stretch",
            ):
                st.session_state[page_key] += 1
                st.rerun()
            page_programs, _, _ = paginate_results(
                programs_to_show, st.session_state[page_key]
            )
            for row_start in range(0, len(page_programs), 2):
                card_columns = st.columns(2)
                for column, (_, program) in zip(
                    card_columns,
                    page_programs.iloc[row_start : row_start + 2].iterrows(),
                ):
                    with column:
                        deadline = program["application_deadline_final"]
                        deadline_text = (
                            str(deadline) if pd.notna(deadline) else t("Not published")
                        )
                        with st.container(border=True):
                            st.markdown(
                                f"<div class='op-card-status'>{status_icons[program['eligibility_status']]}</div>",
                                unsafe_allow_html=True,
                            )
                            st.markdown(f"### {program['university']}")
                            st.markdown(f"**{program['program']}**")
                            st.caption(
                                f"{t(str(program['country']))} · "
                                f"{t(str(program['field_category']))} · {program['intake']}"
                            )
                            fee_col, deadline_col = st.columns(2)
                            fee_col.metric(
                                t("Estimated fees"),
                                f"${int(program['estimated_first_year_fees_usd']):,}",
                            )
                            deadline_col.metric(t("Deadline"), deadline_text)
                            st.caption(t(str(program["eligibility_summary"])))
                            if st.button(
                                t("View details"),
                                key=f"details::{program['university']}::{program['program']}",
                                width="stretch",
                            ):
                                show_program_dialog(program)
        else:
            st.dataframe(
                programs_to_show[
                    [
                        "status_display",
                        "university",
                        "program",
                        "country_display",
                        "estimated_first_year_fees_usd",
                        "aid_model_display",
                        "application_deadline_final",
                    ]
                ],
                hide_index=True,
                width="stretch",
                column_config={
                    "status_display": t("Result"),
                    "university": t("University"),
                    "program": t("Program"),
                    "country_display": t("Country"),
                    "estimated_first_year_fees_usd": st.column_config.NumberColumn(
                        t("Estimated fees"), format="$%d"
                    ),
                    "aid_model_display": t("Aid model"),
                    "application_deadline_final": st.column_config.DateColumn(
                        t("Deadline")
                    ),
                },
            )

            detail_options = programs_to_show.index.tolist()
            selected_detail = st.selectbox(
                t("Select a program to view details"),
                options=detail_options,
                format_func=lambda index: (
                    f"{programs_to_show.loc[index, 'university']} — "
                    f"{programs_to_show.loc[index, 'program']}"
                ),
            )
            if st.button(t("View details"), key="table_details", width="stretch"):
                show_program_dialog(programs_to_show.loc[selected_detail])

with shortlist_tab:
    st.divider()
    st.subheader(t("Your shortlist"))
    keyed_programs = add_program_keys(all_evaluated)
    program_labels = (
        keyed_programs.set_index("program_key")
        .apply(
            lambda row: f"{row['university']} — {row['program']} ({row['country']})",
            axis=1,
        )
        .to_dict()
    )
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        shortlist_countries = st.multiselect(
            t("Filter by country"),
            options=sorted(keyed_programs["country"].dropna().unique()),
            format_func=t,
            placeholder=t("All countries"),
        )
    with filter_col2:
        shortlist_fields = st.multiselect(
            t("Filter by field"),
            options=sorted(keyed_programs["field_category"].dropna().unique()),
            format_func=t,
            placeholder=t("All fields"),
        )

    shortlist_choices = keyed_programs.copy()
    if shortlist_countries:
        shortlist_choices = shortlist_choices[
            shortlist_choices["country"].isin(shortlist_countries)
        ]
    if shortlist_fields:
        shortlist_choices = shortlist_choices[
            shortlist_choices["field_category"].isin(shortlist_fields)
        ]
    existing_choices = st.session_state.get("shortlist_program_keys", [])
    available_keys = shortlist_choices["program_key"].tolist()
    available_keys.extend(key for key in existing_choices if key not in available_keys)

    selected_program_keys = st.multiselect(
        t("Add programs to compare"),
        options=available_keys,
        format_func=lambda key: program_labels[key],
        key="shortlist_program_keys",
        placeholder=t("Choose one or more programs"),
    )
    st.caption(
        t(
            "Use the country and field filters to narrow the list. Start typing to search by university or program name."
        )
    )

    shortlist = build_shortlist(all_evaluated, selected_program_keys)
    if shortlist.empty:
        st.info(t("Select programs above to build a personal comparison list."))
    else:
        upcoming_deadline = next_deadline(shortlist)
        shortlist_col1, shortlist_col2, shortlist_col3 = st.columns(3)
        shortlist_col1.metric(t("Selected programs"), len(shortlist))
        shortlist_col2.metric(t("Countries"), shortlist["country"].nunique())
        shortlist_col3.metric(
            t("Next deadline"),
            upcoming_deadline.strftime("%Y-%m-%d")
            if upcoming_deadline is not None
            else t("No upcoming date"),
        )

        shortlist_display = shortlist.copy()
        shortlist_display["status_display"] = shortlist_display[
            "eligibility_status"
        ].map(
            {
                "Eligible": f"🟢 {t('Eligible')}",
                "Conditional": f"🟡 {t('Conditional')}",
                "Not eligible": f"🔴 {t('Not eligible')}",
            }
        )
        shortlist_display["country_display"] = shortlist_display["country"].map(t)
        shortlist_display["aid_model_display"] = shortlist_display["aid_model"].map(t)
        shortlist_display["living_costs_display"] = shortlist_display[
            "aid_covers_living_costs"
        ].map(t)
        shortlist_display["summary_display"] = shortlist_display[
            "eligibility_summary"
        ].map(t)
        st.dataframe(
            shortlist_display[
                [
                    "status_display",
                    "university",
                    "program",
                    "country_display",
                    "estimated_first_year_fees_usd",
                    "aid_model_display",
                    "living_costs_display",
                    "summary_display",
                    "application_deadline_final",
                ]
            ],
            hide_index=True,
            width="stretch",
            column_config={
                "status_display": t("Result"),
                "university": t("University"),
                "program": t("Program"),
                "country_display": t("Country"),
                "estimated_first_year_fees_usd": st.column_config.NumberColumn(
                    t("Estimated first-year fees"), format="$%d"
                ),
                "aid_model_display": t("Aid model"),
                "living_costs_display": t("Living costs"),
                "summary_display": t("Remaining issue"),
                "application_deadline_final": st.column_config.DateColumn(
                    t("Deadline")
                ),
            },
        )
        st.download_button(
            t("Download shortlist as Excel"),
            data=shortlist_xlsx(shortlist),
            file_name="openpath_shortlist.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

        st.subheader(t("Application timeline"))
        st.caption(
            t(
                "Official university dates and OpenPath planning milestones are labelled separately. Planning dates are recommendations, not additional deadlines."
            )
        )
        timeline = build_application_timeline(shortlist)
        upcoming_only = st.checkbox(t("Show upcoming events only"), value=True)
        timeline_to_show = timeline.copy()
        if not timeline_to_show.empty:
            timeline_to_show["event"] = timeline_to_show["event"].map(t)
            timeline_to_show["date_type"] = timeline_to_show["date_type"].map(t)
            timeline_to_show["note"] = timeline_to_show["note"].map(t)
            timeline_to_show["timing"] = timeline_to_show["days_remaining"].map(
                timing_text
            )
        if upcoming_only:
            timeline_to_show = timeline_to_show[timeline_to_show["days_remaining"] >= 0]

        next_event = next_timeline_event(timeline)
        if next_event is not None:
            st.info(
                f"{t('Next action')}: {t(next_event['event'])} {t('for')} {next_event['university']} "
                f"{t('on')} {next_event['event_date']:%Y-%m-%d} ({timing_text(next_event['days_remaining'])})."
            )
        else:
            st.warning(
                t("There are no upcoming dated events in the current shortlist.")
            )

        if timeline_to_show.empty:
            st.warning(t("No timeline events match the current view."))
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
                    "event_date": st.column_config.DateColumn(t("Date")),
                    "timing": t("Timing"),
                    "university": t("University"),
                    "program": t("Program"),
                    "event": t("Action"),
                    "date_type": t("Date type"),
                    "note": t("Details"),
                    "source": st.column_config.LinkColumn(t("Official source")),
                },
            )

        st.download_button(
            t("Download application timeline as Excel"),
            data=timeline_xlsx(timeline),
            file_name="openpath_application_timeline.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

        st.subheader(t("Application checklist"))
        st.caption(
            t(
                "This checklist is generated only from requirements already recorded in OpenPath. Always confirm the final document list on the official website. Progress is saved for the current browser session."
            )
        )
        checklist = build_application_checklist(shortlist)
        completed_task_keys = {
            task_key
            for task_key in checklist["task_key"]
            if st.session_state.get(f"checklist::{task_key}", False)
        }
        completed_tasks, total_tasks, progress_percent = checklist_progress(
            checklist, completed_task_keys
        )
        st.write(
            f"**{t('Overall progress')}:** {completed_tasks}/{total_tasks} {t('tasks')}"
        )
        st.progress(progress_percent / 100, text=f"{progress_percent}% {t('complete')}")

        for program_key, program_tasks in checklist.groupby("program_key", sort=False):
            university = program_tasks.iloc[0]["university"]
            program_name = program_tasks.iloc[0]["program"]
            program_completed_keys = {
                task_key
                for task_key in program_tasks["task_key"]
                if st.session_state.get(f"checklist::{task_key}", False)
            }
            program_completed, program_total, _ = checklist_progress(
                program_tasks, program_completed_keys
            )
            with st.container(border=True):
                st.markdown(
                    f"**{university} — {program_name} ({program_completed}/{program_total})**"
                )
                for _, task in program_tasks.iterrows():
                    st.checkbox(
                        f"{t(task['task'])} · {t(task['requirement_type'])}",
                        key=f"checklist::{task['task_key']}",
                    )
                    st.caption(t(task["note"]))
                st.link_button(
                    t("Verify requirements at the official source"),
                    program_tasks.iloc[0]["source"],
                )

st.subheader(t("Sources and limitations"))
st.write(
    t(
        "OpenPath does not treat missing information as zero and does not predict "
        "scholarship probability without reliable historical decision data."
    )
)
