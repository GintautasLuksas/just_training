# SQL 30 Min Trainer

A small PostgreSQL-backed Streamlit app for daily SQL practice.

The app gives you a focused 30 minute session, runs your query against a fresh practice schema, and checks the returned result against an expected result. Your SQL does not need to match the solution text exactly; it needs to return the correct table.

## Setup

1. Create a PostgreSQL database, for example `sql_training`.
2. Copy `.env.example` to `.env`.
3. Fill in your PostgreSQL connection values.
4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Run the app:

```powershell
streamlit run app.py
```

On first launch the app creates:

- `sql_trainer.tasks`
- `sql_trainer.attempts`
- a temporary `practice` schema that is reset for each task

## Daily Flow

- Open the app.
- Click **Build new 30 min session** when you want a fresh set.
- Solve tasks in order.
- Use **Run** to preview your result.
- Use **Check** to compare your result with the expected result.
- Use **Solution** only after you have tried the task.

## Adding Tasks In The App

Use **Task Manager** in the sidebar.

- **Add Task** validates setup SQL and expected SQL before saving.
- **Export** downloads all tasks from PostgreSQL as `sql_trainer_tasks.json`.
- **Import** loads that JSON on this or another computer.

Tasks added through the browser are saved in PostgreSQL, not automatically written back into `sql_trainer/seed_data.py`. Use Export/Import when you want to back them up or move them to another machine.

## What It Teaches First

The seed tasks are based on the old `src/old_sql.txt` practice style:

- `COUNT(*)` vs `COUNT(column)`
- filtering with `WHERE`
- `GROUP BY`
- `HAVING`
- `COALESCE`
- `COUNT(DISTINCT ...)`
- `JOIN` and `LEFT JOIN`
- aggregate subqueries

## Safety

Practice attempts only allow `SELECT` and `WITH` queries. The app recreates the `practice` schema for every task, so each exercise starts from clean data.
