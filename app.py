import json
import pandas as pd
import streamlit as st

from sql_trainer.config import get_settings
from sql_trainer.db import (
    check_answer,
    get_all_tasks,
    get_daily_tasks,
    get_practice_tables,
    get_progress,
    init_metadata,
    make_engine,
    record_attempt,
    reset_practice_schema,
    run_query,
    save_task,
    seed_tasks,
    validate_task_definition,
)
from sql_trainer.seed_data import SEED_TASKS


st.set_page_config(page_title="SQL 30 Min Trainer", page_icon="SQL", layout="wide")

st.markdown(
    """
    <style>
    .practice-table {
        display: flex;
        justify-content: center;
        width: 100%;
        overflow-x: auto;
        padding: 0;
    }
    .table-title {
        text-align: center;
        font-weight: 700;
        margin: 0;
        padding: 0.35rem 0.5rem;
        color: #111827;
        background: #e5e7eb;
        border: 1px solid #cbd5e1;
        border-bottom: 0;
        border-radius: 6px 6px 0 0;
    }
    .table-card {
        border-radius: 6px;
        margin-bottom: 0.75rem;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }
    .practice-table table {
        border-collapse: collapse;
        width: 100%;
        font-size: 0.92rem;
        color: #111827;
        background: #ffffff;
    }
    .practice-table th,
    .practice-table td {
        border: 1px solid #cbd5e1;
        padding: 0.38rem 0.65rem;
        text-align: center;
        white-space: nowrap;
    }
    .practice-table th {
        color: #111827;
        background: #f3f4f6;
        font-weight: 700;
    }
    .practice-table td {
        color: #111827;
        background: #ffffff;
    }
    .practice-table tr:nth-child(even) td {
        background: #f9fafb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_runtime():
    settings = get_settings()
    engine = make_engine(settings)
    init_metadata(engine, settings)
    seed_tasks(engine, settings, SEED_TASKS)
    return settings, engine


def ensure_daily_session(engine, settings):
    if "daily_tasks" not in st.session_state:
        st.session_state.daily_tasks = get_daily_tasks(engine, settings, minutes=30)
        st.session_state.task_index = 0
        st.session_state.last_result = None


def current_task():
    tasks = st.session_state.daily_tasks
    if not tasks:
        return None
    return tasks[min(st.session_state.task_index, len(tasks) - 1)]


def show_result(result):
    if result.is_correct:
        st.success(result.message)
    else:
        st.error(result.message)
    if result.error:
        st.code(result.error, language="text")
    if result.user_df is not None:
        st.markdown("**Your result**")
        show_readable_table("Your result", result.user_df, show_title=False)
        st.markdown("**Expected result**")
        show_readable_table("Expected result", result.expected_df, show_title=False)


def format_concepts(concepts):
    return ", ".join(str(concept) for concept in (concepts or []) if concept)


def show_readable_table(title, data, show_title=True):
    if data is None:
        return
    html = data.to_html(index=False, escape=True, border=0)
    title_html = f'<div class="table-title">{title}</div>' if show_title else ""
    st.markdown(
        f"""
        <div class="table-card">
            {title_html}
            <div class="practice-table">{html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def run_preview(engine, settings, task, submitted_sql):
    reset_practice_schema(engine, settings, task["setup_sql"])
    return run_query(engine, settings, submitted_sql)


def show_practice_tables(engine, settings, task):
    reset_practice_schema(engine, settings, task["setup_sql"])
    tables = get_practice_tables(engine, settings)
    if not tables:
        st.info("No practice tables found for this task.")
        return
    st.caption(f"This task uses {len(tables)} table{'s' if len(tables) != 1 else ''}.")
    table_items = list(tables.items())
    for start in range(0, len(table_items), 2):
        columns = st.columns(min(2, len(table_items) - start))
        for column, (table_name, data) in zip(columns, table_items[start : start + 2]):
            with column:
                show_readable_table(table_name, data)


def clean_slug(value):
    return value.strip().lower().replace(" ", "-")


def parse_concepts(value):
    return [item.strip().lower() for item in value.split(",") if item.strip()]


def task_manager(engine, settings):
    st.title("Task Manager")
    st.caption("Add tasks in the browser, validate them, export them, and import them on another computer.")

    all_tasks = get_all_tasks(engine, settings)
    st.metric("Task bank", len(all_tasks))

    tab_add, tab_export, tab_import = st.tabs(["Add Task", "Export", "Import"])

    with tab_add:
        with st.form("add_task_form"):
            title = st.text_input("Title", placeholder="Average Spending Per Customer")
            slug = st.text_input("Slug", placeholder="average-spending-per-customer")
            prompt = st.text_area("Prompt", height=90, placeholder="Return customer_name and avg_spent...")
            setup_sql = st.text_area("Setup SQL", height=180, placeholder="CREATE TABLE ...\nINSERT INTO ...")
            expected_sql = st.text_area("Expected SQL", height=120, placeholder="SELECT ...")
            solution_sql = st.text_area("Solution SQL", height=120, placeholder="SELECT ...")
            hint = st.text_input("Hint 1", placeholder="Use GROUP BY after joining customers to orders.")
            hint2 = st.text_area("Hint 2", height=90, placeholder="Show customer_name and total_spent. Join customers to orders, group by customer, and sort by total_spent descending.")
            concepts = st.text_input("Concepts", placeholder="join, group by, avg")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                difficulty = st.slider("Difficulty", 1, 4, 2)
            with col_b:
                estimated_minutes = st.number_input("Minutes", min_value=1, max_value=30, value=6)
            with col_c:
                sort_order = st.number_input("Sort order", min_value=0, value=5000)
            action = st.radio("Action", ["Validate only", "Validate and save"], horizontal=True)
            submitted = st.form_submit_button("Run")

        if submitted:
            new_task = {
                "slug": clean_slug(slug or title),
                "title": title.strip(),
                "prompt": prompt.strip(),
                "setup_sql": setup_sql.strip(),
                "expected_sql": expected_sql.strip(),
                "solution_sql": solution_sql.strip() or expected_sql.strip(),
                "hint": hint.strip(),
                "hint2": hint2.strip(),
                "concepts": parse_concepts(concepts),
                "difficulty": int(difficulty),
                "estimated_minutes": int(estimated_minutes),
                "sort_order": int(sort_order),
            }
            result = validate_task_definition(engine, settings, new_task)
            if result.is_correct:
                st.success(result.message)
                if result.expected_df is not None:
                    st.caption("Expected result preview")
                    st.dataframe(result.expected_df, use_container_width=True)
                if action == "Validate and save":
                    save_task(engine, settings, new_task)
                    st.success(f"Saved task: {new_task['slug']}")
                    st.cache_resource.clear()
            else:
                st.error(result.message)
                if result.error:
                    st.code(result.error, language="text")

    with tab_export:
        export_payload = json.dumps(all_tasks, indent=2)
        st.download_button(
            "Download tasks JSON",
            data=export_payload,
            file_name="sql_trainer_tasks.json",
            mime="application/json",
            use_container_width=True,
        )
        st.caption("This includes built-in and browser-added tasks from PostgreSQL.")
        st.text_area("Export preview", export_payload[:5000], height=260)

    with tab_import:
        uploaded = st.file_uploader("Import tasks JSON", type=["json"])
        if uploaded is not None:
            try:
                imported_tasks = json.loads(uploaded.read().decode("utf-8"))
                if not isinstance(imported_tasks, list):
                    raise ValueError("JSON must contain a list of task objects.")
                st.info(f"Found {len(imported_tasks)} tasks in file.")
                if st.button("Validate and import", type="primary"):
                    failures = []
                    for imported_task in imported_tasks:
                        imported_task["concepts"] = imported_task.get("concepts") or []
                        imported_task["difficulty"] = int(imported_task.get("difficulty", 1))
                        imported_task["estimated_minutes"] = int(imported_task.get("estimated_minutes", 5))
                        imported_task["sort_order"] = int(imported_task.get("sort_order", 0))
                        result = validate_task_definition(engine, settings, imported_task)
                        if result.is_correct:
                            save_task(engine, settings, imported_task)
                        else:
                            failures.append((imported_task.get("slug", "unknown"), result.error or result.message))
                    if failures:
                        st.error(f"Imported with {len(failures)} failures.")
                        for slug, error in failures[:10]:
                            st.code(f"{slug}: {error}", language="text")
                    else:
                        st.success("All tasks imported.")
                        st.cache_resource.clear()
            except Exception as exc:
                st.error("Could not read import file.")
                st.code(str(exc), language="text")


try:
    settings, engine = get_runtime()
except Exception as exc:
    st.title("SQL 30 Min Trainer")
    st.error("Database connection is not ready.")
    st.code(str(exc), language="text")
    st.markdown(
        "Create a `.env` file from `.env.example`, set your PostgreSQL values, "
        "then restart Streamlit."
    )
    st.stop()

ensure_daily_session(engine, settings)
progress = get_progress(engine, settings)

with st.sidebar:
    st.title("SQL Trainer")
    st.caption("30 minutes a day, inside PostgreSQL.")
    page = st.radio("Page", ["Practice", "Task Manager"])
    st.metric("Solved", f"{progress.get('solved_tasks') or 0}/{progress.get('total_tasks') or 0}")
    st.metric("Attempts today", progress.get("attempts_today") or 0)
    st.metric("All attempts", progress.get("total_attempts") or 0)
    if st.button("Build new 30 min session", use_container_width=True):
        st.session_state.daily_tasks = get_daily_tasks(engine, settings, minutes=30)
        st.session_state.task_index = 0
        st.session_state.last_result = None
        st.rerun()

if page == "Task Manager":
    task_manager(engine, settings)
    st.stop()

task = current_task()
if task is None:
    st.title("SQL 30 Min Trainer")
    st.info("No tasks found. The seed step may not have completed.")
    st.stop()

task_count = len(st.session_state.daily_tasks)
task_number = st.session_state.task_index + 1
task_minutes = sum(int(item["estimated_minutes"]) for item in st.session_state.daily_tasks)

header_left, header_right = st.columns([3, 1])
with header_left:
    st.title("SQL 30 Min Trainer")
    st.caption(f"Daily set: {task_count} tasks, about {task_minutes} minutes")
with header_right:
    st.metric("Current task", f"{task_number}/{task_count}")

st.divider()

run_clicked = False
check_clicked = False
solution_clicked = False

task_workspace, table_panel = st.columns([1.05, 1.35], gap="medium")
with task_workspace:
    st.subheader(task["title"])
    st.write(task["prompt"])
    concept_labels = format_concepts(task["concepts"])
    st.caption(
        f"Difficulty {int(task['difficulty'])}/4 | "
        f"{int(task['estimated_minutes'])} min | {concept_labels}"
    )

    with st.expander("Hint 1", expanded=False):
        st.write(task["hint"] or "No first hint for this task.")

    with st.expander("Hint 2", expanded=False):
        if task.get("hint2"):
            st.write(task["hint2"])
        else:
            st.caption("No second hint for this task.")

    st.markdown("**Your SQL**")
    query_key = f"query_text_{task['id']}"
    submitted_sql = st.text_area(
        "Your SQL",
        key=query_key,
        height=300,
        placeholder="SELECT ...",
        label_visibility="collapsed",
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        run_clicked = st.button("Run", type="secondary", use_container_width=True)
    with col2:
        check_clicked = st.button("Check", type="primary", use_container_width=True)

    if run_clicked:
        try:
            preview = run_preview(engine, settings, task, submitted_sql)
            st.caption("Query result")
            show_readable_table("Query result", preview, show_title=False)
        except Exception as exc:
            st.error("Query failed.")
            st.code(str(exc), language="text")

    if check_clicked:
        result = check_answer(engine, settings, task, submitted_sql)
        record_attempt(engine, settings, int(task["id"]), submitted_sql, result)
        st.session_state.last_result = result
        show_result(result)

    if st.session_state.last_result is not None and not (run_clicked or check_clicked):
        show_result(st.session_state.last_result)

with table_panel:
    st.markdown("**Practice Tables**")
    show_practice_tables(engine, settings, task)

    solution_clicked = st.button("Solution", use_container_width=True)
    if solution_clicked:
        st.code(task["solution_sql"], language="sql")

    with st.expander("Setup SQL"):
        st.code(task["setup_sql"], language="sql")

    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("Previous", use_container_width=True, disabled=st.session_state.task_index == 0):
            st.session_state.task_index -= 1
            st.session_state.last_result = None
            st.rerun()
    with nav2:
        if st.session_state.task_index >= task_count - 1:
            if st.button("Finish session", type="primary", use_container_width=True):
                st.success("Session complete. Nice work.")
                st.session_state.daily_tasks = get_daily_tasks(engine, settings, minutes=30)
                st.session_state.task_index = 0
                st.session_state.last_result = None
                st.rerun()
        elif st.button("Next", use_container_width=True):
            st.session_state.task_index += 1
            st.session_state.last_result = None
            st.rerun()

    if st.session_state.last_result is not None and st.session_state.last_result.is_correct:
        st.info("Good. Move to the next task while the idea is still warm.")

with st.expander("Today list", expanded=False):
    today = pd.DataFrame(
        [
            {
                "task": item["title"],
                "difficulty": item["difficulty"],
                "minutes": item["estimated_minutes"],
                "concepts": format_concepts(item["concepts"]),
            }
            for item in st.session_state.daily_tasks
        ]
    )
    st.dataframe(today, use_container_width=True, hide_index=True)
