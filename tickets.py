"""Offline help desk ticket tracker using Python's standard library and SQLite."""
import argparse
import csv
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

PRIORITIES = ('low', 'medium', 'high', 'critical')
STATUSES = ('open', 'in_progress', 'resolved')


def connect(database):
    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    db.execute('''CREATE TABLE IF NOT EXISTS tickets (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title TEXT NOT NULL CHECK(length(trim(title)) > 0),
       description TEXT NOT NULL DEFAULT '',
       requester TEXT NOT NULL,
       priority TEXT NOT NULL CHECK(priority IN ('low','medium','high','critical')),
       status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','in_progress','resolved')),
       created_at TEXT NOT NULL,
       updated_at TEXT NOT NULL
    )''')
    db.commit()
    return db


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def create_ticket(db, title, requester, description='', priority='medium'):
    if not title.strip() or not requester.strip():
        raise ValueError('Title and requester cannot be blank')
    if priority not in PRIORITIES:
        raise ValueError('Invalid priority')
    now = timestamp()
    cursor = db.execute('''INSERT INTO tickets
        (title,description,requester,priority,status,created_at,updated_at)
        VALUES (?,?,?,?,'open',?,?)''',
        (title.strip(), description.strip(), requester.strip(), priority, now, now))
    db.commit()
    return cursor.lastrowid


def change_status(db, ticket_id, status):
    if status not in STATUSES:
        raise ValueError('Invalid status')
    cursor = db.execute('UPDATE tickets SET status=?, updated_at=? WHERE id=?',
                        (status, timestamp(), ticket_id))
    db.commit()
    if cursor.rowcount == 0:
        raise LookupError(f'Ticket {ticket_id} does not exist')


def list_tickets(db, status=None, search=None):
    sql = 'SELECT * FROM tickets WHERE 1=1'
    params = []
    if status:
        if status not in STATUSES:
            raise ValueError('Invalid status')
        sql += ' AND status=?'
        params.append(status)
    if search:
        sql += ' AND (title LIKE ? OR description LIKE ? OR requester LIKE ?)'
        params.extend([f'%{search}%'] * 3)
    sql += ' ORDER BY CASE priority WHEN "critical" THEN 1 WHEN "high" THEN 2 WHEN "medium" THEN 3 ELSE 4 END, id DESC'
    return db.execute(sql, params).fetchall()


def summary(db):
    total = db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0]
    by_status = {name: 0 for name in STATUSES}
    for row in db.execute('SELECT status, COUNT(*) AS n FROM tickets GROUP BY status'):
        by_status[row['status']] = row['n']
    return {'total': total, **by_status}


def export_csv(db, output):
    records = db.execute('SELECT * FROM tickets ORDER BY id').fetchall()
    fields = ('id', 'title', 'description', 'requester', 'priority', 'status', 'created_at', 'updated_at')
    with open(output, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        for row in records:
            writer.writerow([row[field] for field in fields])
    return len(records)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', default='tickets.db', help='Path to local SQLite database')
    sub = parser.add_subparsers(dest='command', required=True)
    create = sub.add_parser('new', help='Create a support ticket')
    create.add_argument('title')
    create.add_argument('--requester', required=True)
    create.add_argument('--priority', choices=PRIORITIES, default='medium')
    create.add_argument('--description', default='')
    listing = sub.add_parser('list', help='List and search tickets')
    listing.add_argument('--status', choices=STATUSES)
    listing.add_argument('--search')
    update = sub.add_parser('status', help='Update ticket status')
    update.add_argument('id', type=int)
    update.add_argument('value', choices=STATUSES)
    sub.add_parser('summary', help='Report ticket counts')
    export = sub.add_parser('export', help='Export data to CSV')
    export.add_argument('path')
    args = parser.parse_args(argv)
    with connect(args.db) as db:
        if args.command == 'new':
            print(f'Created ticket #{create_ticket(db, args.title, args.requester, args.description, args.priority)}')
        elif args.command == 'list':
            for item in list_tickets(db, args.status, args.search):
                print(f"#{item['id']} [{item['priority']}] [{item['status']}] {item['title']} - {item['requester']}")
        elif args.command == 'status':
            change_status(db, args.id, args.value)
            print(f'Ticket #{args.id} updated to {args.value}')
        elif args.command == 'summary':
            report = summary(db)
            print(' | '.join(f'{key}: {value}' for key, value in report.items()))
        elif args.command == 'export':
            print(f'Exported {export_csv(db, args.path)} tickets to {args.path}')


if __name__ == '__main__':
    main()
