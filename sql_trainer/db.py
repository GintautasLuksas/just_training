from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
import re
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .config import Settings


FORBIDDEN_SQL = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|copy|call|execute)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CheckResult:
    is_correct: bool
    message: str
    user_df: pd.DataFrame | None = None
    expected_df: pd.DataFrame | None = None
    error: str | None = None


def make_engine(settings: Settings) -> Engine:
    return create_engine(settings.sqlalchemy_url, pool_pre_ping=True)


def init_metadata(engine: Engine, settings: Settings) -> None:
    schema = settings.app_schema
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        conn.execute(
            text(
                f"""
                CREATE TABLE IF NOT EXISTS "{schema}".tasks (
                    id SERIAL PRIMARY KEY,
                    slug TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    setup_sql TEXT NOT NULL,
                    expected_sql TEXT NOT NULL,
                    solution_sql TEXT NOT NULL,
                    hint TEXT NOT NULL DEFAULT '',
                    hint2 TEXT NOT NULL DEFAULT '',
                    concepts TEXT[] NOT NULL DEFAULT '{{}}',
                    difficulty INTEGER NOT NULL DEFAULT 1,
                    estimated_minutes INTEGER NOT NULL DEFAULT 5,
                    sort_order INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )
        conn.execute(text(f'ALTER TABLE "{schema}".tasks ADD COLUMN IF NOT EXISTS hint2 TEXT NOT NULL DEFAULT \'\''))
        conn.execute(
            text(
                f"""
                CREATE TABLE IF NOT EXISTS "{schema}".attempts (
                    id SERIAL PRIMARY KEY,
                    task_id INTEGER NOT NULL REFERENCES "{schema}".tasks(id),
                    submitted_sql TEXT NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    error TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )


def seed_tasks(engine: Engine, settings: Settings, tasks: list[dict[str, Any]]) -> None:
    schema = settings.app_schema
    with engine.begin() as conn:
        for task in tasks:
            conn.execute(
                text(
                    f"""
                    INSERT INTO "{schema}".tasks (
                        slug, title, prompt, setup_sql, expected_sql, solution_sql,
                        hint, hint2, concepts, difficulty, estimated_minutes, sort_order
                    )
                    VALUES (
                        :slug, :title, :prompt, :setup_sql, :expected_sql, :solution_sql,
                        :hint, :hint2, :concepts, :difficulty, :estimated_minutes, :sort_order
                    )
                    ON CONFLICT (slug) DO UPDATE SET
                        title = EXCLUDED.title,
                        prompt = EXCLUDED.prompt,
                        setup_sql = EXCLUDED.setup_sql,
                        expected_sql = EXCLUDED.expected_sql,
                        solution_sql = EXCLUDED.solution_sql,
                        hint = EXCLUDED.hint,
                        hint2 = EXCLUDED.hint2,
                        concepts = EXCLUDED.concepts,
                        difficulty = EXCLUDED.difficulty,
                        estimated_minutes = EXCLUDED.estimated_minutes,
                        sort_order = EXCLUDED.sort_order
                    """
                ),
                {**task, "hint2": task.get("hint2", "")},
            )


def save_task(engine: Engine, settings: Settings, task: dict[str, Any]) -> None:
    seed_tasks(engine, settings, [task])


def get_all_tasks(engine: Engine, settings: Settings) -> list[dict[str, Any]]:
    schema = settings.app_schema
    df = pd.read_sql_query(
        text(
            f"""
            SELECT
                slug, title, prompt, setup_sql, expected_sql, solution_sql,
                hint, hint2, concepts, difficulty, estimated_minutes, sort_order
            FROM "{schema}".tasks
            ORDER BY sort_order, id
            """
        ),
        engine,
    )
    tasks = df.to_dict("records")
    for task in tasks:
        task["concepts"] = [concept for concept in (task.get("concepts") or []) if concept]
        task["difficulty"] = int(task["difficulty"])
        task["estimated_minutes"] = int(task["estimated_minutes"])
        task["sort_order"] = int(task["sort_order"])
    return tasks


def validate_task_definition(engine: Engine, settings: Settings, task: dict[str, Any]) -> CheckResult:
    required_fields = [
        "slug",
        "title",
        "prompt",
        "setup_sql",
        "expected_sql",
        "solution_sql",
    ]
    missing = [field for field in required_fields if not str(task.get(field, "")).strip()]
    if missing:
        message = f"Missing required fields: {', '.join(missing)}"
        return CheckResult(False, message, error=message)
    slug = str(task["slug"]).strip()
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
        message = "Slug must use lowercase letters, numbers, and hyphens only."
        return CheckResult(False, message, error=message)
    validation_error = validate_select(task["expected_sql"])
    if validation_error:
        return CheckResult(False, validation_error, error=validation_error)
    try:
        reset_practice_schema(engine, settings, task["setup_sql"])
        expected_df = run_query(engine, settings, task["expected_sql"])
        return CheckResult(True, "Task is valid. Setup SQL runs and expected SQL returns a result.", expected_df=expected_df)
    except Exception as exc:
        return CheckResult(False, "Task validation failed.", error=str(exc))


def get_daily_tasks(engine: Engine, settings: Settings, minutes: int = 30) -> list[dict[str, Any]]:
    schema = settings.app_schema
    query = text(
        f"""
        WITH stats AS (
            SELECT
                t.id,
                COUNT(a.id) AS attempts,
                COUNT(a.id) FILTER (WHERE a.is_correct) AS correct_attempts,
                MAX(a.created_at) AS last_attempt_at
            FROM "{schema}".tasks t
            LEFT JOIN "{schema}".attempts a ON a.task_id = t.id
            GROUP BY t.id
        )
        SELECT
            t.*,
            COALESCE(s.attempts, 0) AS attempts,
            COALESCE(s.correct_attempts, 0) AS correct_attempts,
            s.last_attempt_at
        FROM "{schema}".tasks t
        JOIN stats s ON s.id = t.id
        ORDER BY
            CASE WHEN s.correct_attempts = 0 THEN 0 ELSE 1 END,
            s.last_attempt_at NULLS FIRST,
            t.difficulty,
            t.sort_order
        """
    )
    tasks = pd.read_sql_query(query, engine).to_dict("records")
    selected: list[dict[str, Any]] = []
    total = 0
    for task in tasks:
        if selected and total + int(task["estimated_minutes"]) > minutes:
            continue
        selected.append(task)
        total += int(task["estimated_minutes"])
        if total >= minutes:
            break
    return selected


def get_task_by_id(engine: Engine, settings: Settings, task_id: int) -> dict[str, Any] | None:
    schema = settings.app_schema
    df = pd.read_sql_query(
        text(f'SELECT * FROM "{schema}".tasks WHERE id = :task_id'),
        engine,
        params={"task_id": task_id},
    )
    if df.empty:
        return None
    return df.iloc[0].to_dict()


def get_progress(engine: Engine, settings: Settings) -> dict[str, int]:
    schema = settings.app_schema
    with engine.begin() as conn:
        row = conn.execute(
            text(
                f"""
                SELECT
                    (SELECT COUNT(*) FROM "{schema}".tasks) AS total_tasks,
                    COUNT(DISTINCT task_id) FILTER (WHERE is_correct) AS solved_tasks,
                    COUNT(*) AS total_attempts,
                    COUNT(*) FILTER (
                        WHERE created_at::date = CURRENT_DATE
                    ) AS attempts_today
                FROM "{schema}".attempts
                """
            )
        ).mappings().one()
    return dict(row)


def reset_practice_schema(engine: Engine, settings: Settings, setup_sql: str) -> None:
    practice_schema = settings.practice_schema
    with engine.begin() as conn:
        conn.execute(text(f'DROP SCHEMA IF EXISTS "{practice_schema}" CASCADE'))
        conn.execute(text(f'CREATE SCHEMA "{practice_schema}"'))
        conn.execute(text(f'SET search_path TO "{practice_schema}"'))
        for statement in split_sql_statements(setup_sql):
            conn.execute(text(statement))


def split_sql_statements(sql: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    in_single_quote = False
    previous = ""
    for char in sql:
        if char == "'" and previous != "\\":
            in_single_quote = not in_single_quote
        if char == ";" and not in_single_quote:
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(char)
        previous = char
    trailing = "".join(current).strip()
    if trailing:
        statements.append(trailing)
    return statements


def validate_select(sql: str) -> str | None:
    cleaned = sql.strip().rstrip(";")
    if not cleaned:
        return "Write a SELECT query first."
    if not re.match(r"^(select|with)\b", cleaned, re.IGNORECASE | re.DOTALL):
        return "Only SELECT or WITH queries are allowed in practice attempts."
    if FORBIDDEN_SQL.search(cleaned):
        return "This trainer only runs read-only SELECT practice queries."
    return None


def run_query(engine: Engine, settings: Settings, sql: str) -> pd.DataFrame:
    with engine.begin() as conn:
        conn.execute(text(f'SET search_path TO "{settings.practice_schema}"'))
        return pd.read_sql_query(text(sql.strip().rstrip(";")), conn)


def get_practice_tables(engine: Engine, settings: Settings) -> dict[str, pd.DataFrame]:
    table_names = pd.read_sql_query(
        text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = :schema
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
        ),
        engine,
        params={"schema": settings.practice_schema},
    )["table_name"].tolist()

    tables: dict[str, pd.DataFrame] = {}
    with engine.begin() as conn:
        conn.execute(text(f'SET search_path TO "{settings.practice_schema}"'))
        for table_name in table_names:
            safe_name = table_name.replace('"', '""')
            tables[table_name] = pd.read_sql_query(
                text(f'SELECT * FROM "{safe_name}" ORDER BY 1'),
                conn,
            )
    return tables


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [str(col).lower() for col in normalized.columns]
    normalized = normalized.applymap(
        lambda value: float(value)
        if isinstance(value, Decimal) and value % 1
        else int(value)
        if isinstance(value, Decimal)
        else value
    )
    for col in normalized.columns:
        if pd.api.types.is_float_dtype(normalized[col]):
            normalized[col] = normalized[col].round(6)
    return normalized.where(pd.notnull(normalized), None)


def compare_frames(user_df: pd.DataFrame, expected_df: pd.DataFrame) -> tuple[bool, str]:
    left = normalize_df(user_df)
    right = normalize_df(expected_df)
    if list(left.columns) != list(right.columns):
        return False, "Column names or column order do not match the expected result."
    if left.shape != right.shape:
        return False, f"Expected {right.shape[0]} rows and {right.shape[1]} columns, got {left.shape[0]} rows and {left.shape[1]} columns."
    if not left.equals(right):
        return False, "The result shape is right, but one or more values differ."
    return True, "Correct. Same columns, rows, and values as the expected result."


def check_answer(engine: Engine, settings: Settings, task: dict[str, Any], submitted_sql: str) -> CheckResult:
    validation_error = validate_select(submitted_sql)
    if validation_error:
        return CheckResult(False, validation_error, error=validation_error)
    try:
        reset_practice_schema(engine, settings, task["setup_sql"])
        user_df = run_query(engine, settings, submitted_sql)
        expected_df = run_query(engine, settings, task["expected_sql"])
        is_correct, message = compare_frames(user_df, expected_df)
        return CheckResult(is_correct, message, user_df=user_df, expected_df=expected_df)
    except Exception as exc:
        return CheckResult(False, "Your query raised an error.", error=str(exc))


def record_attempt(
    engine: Engine,
    settings: Settings,
    task_id: int,
    submitted_sql: str,
    result: CheckResult,
) -> None:
    schema = settings.app_schema
    with engine.begin() as conn:
        conn.execute(
            text(
                f"""
                INSERT INTO "{schema}".attempts (task_id, submitted_sql, is_correct, error, created_at)
                VALUES (:task_id, :submitted_sql, :is_correct, :error, :created_at)
                """
            ),
            {
                "task_id": task_id,
                "submitted_sql": submitted_sql,
                "is_correct": result.is_correct,
                "error": result.error,
                "created_at": datetime.now(timezone.utc),
            },
        )
