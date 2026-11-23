# DealerOS reconciliation

A plain Django + React application that imports two event ledgers and shows tenant-safe disagreements.

## Run from a clean clone

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt

cd backend
python manage.py migrate
python manage.py import_data
python manage.py runserver
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

The API is `http://localhost:8000/api/disagreements/?org=ORG-A&reason=VALUE_MISMATCH&sort=-value`.

## Tests

```powershell
cd backend
..\\.venv\\Scripts\\python.exe -m pytest -q
```

## What is built

- Idempotent CSV import for 5 locations, 120 System A rows, and 121 System B rows.
- Raw and parsed values retained in SQLite models.
- Pure comparison logic for missing, orphan, duplicate, value, location, and date disagreements.
- Tenant-filtered API and plain React table with org/reason controls and value sorting.

## Deliberately omitted

Authentication, pagination, Docker, production deployment, and elaborate CSS. These are outside the assignment's small correctness-focused scope.

## How I worked with the agent

I used GitHub Copilot (Copilot SDK in VS Code) for scaffolding, implementation, tests, and documentation. It handled repetitive Django/React structure while I reviewed real CSV counts, data shapes, comparison decisions, and tenant behavior. I verified the work with import counts, repeated imports, pytest, the frontend build, and API checks.

## Three answers

a. **One thing the AI agent got wrong:** In the first migration pass, it accidentally placed Django management-command marker text in a Python package file, which caused a SyntaxError. I noticed the traceback during `migrate`, inspected the generated files, moved the command to `management/commands/import_data.py`, and reran the full setup.

b. **Part I am least confident about:** The cross-org location case is least confident because it depends on a policy choice. I chose to show matched rows under the System A location and never return the conflicting B location in the API. I would add direct real-dataset assertions for every cross-tenant location mismatch.

c. **What I would fix with a second day:** I would add end-to-end browser verification that exercises org switching, filtering, sorting, and network responses, plus stronger tests proving that every payload field is tenant-safe.
