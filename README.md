# Help Desk Ticket Tracker | Python + SQLite

An offline command-line IT support ticket system. Uses **Python 3.9+**, `sqlite3`, `argparse`, and `csv` from the standard library; no installation of third-party packages or cloud accounts required.

## Run
Open a terminal in this folder and run:

```bash
python tickets.py new "Laptop cannot connect to Wi-Fi" --requester "Student Services" --priority high --description "Wireless connection fails after login"
python tickets.py new "Password reset" --requester "Front Desk" --priority medium
python tickets.py list
python tickets.py list --search Wi-Fi
python tickets.py status 1 in_progress
python tickets.py status 1 resolved
python tickets.py summary
python tickets.py export tickets_export.csv
```

The app creates `tickets.db` in the directory. To choose another database file, add `--db path/to/file.db` **before** the subcommand, e.g. `python tickets.py --db demo.db summary`.

## Test

```bash
python -m unittest -v test_tickets.py
```

## Features
- SQLite persistence with input validation and parameterized SQL queries
- Severity ordering, search, and status filtering
- Ticket lifecycle (`open` -> `in_progress` -> `resolved`)
- CSV export and dashboard-style ticket counts
- Unit tests covering creation, status changes, errors, and export

## Further improvements to try yourself
Add ticket assignment, categories, SLA deadlines, user login, or a Streamlit web interface. Never store real customer or patient data in the demo database.

## Interview discussion
Explain why parameterized queries are safer than constructing SQL with user input; why SQLite is useful for local prototypes; and how you would adapt the code for a multi-user help desk.
