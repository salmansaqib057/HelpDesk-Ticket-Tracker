import csv
import tempfile
import unittest
from pathlib import Path
from tickets import connect, create_ticket, change_status, list_tickets, summary, export_csv


class TicketTests(unittest.TestCase):
    def setUp(self):
        self.db = connect(':memory:')

    def tearDown(self):
        self.db.close()

    def test_create_search_and_status(self):
        ticket_id = create_ticket(self.db, 'Printer offline', 'Office A', 'Won\'t print', 'high')
        self.assertEqual(ticket_id, 1)
        self.assertEqual(len(list_tickets(self.db, search='printer')), 1)
        change_status(self.db, ticket_id, 'resolved')
        self.assertEqual(summary(self.db), {'total': 1, 'open': 0, 'in_progress': 0, 'resolved': 1})

    def test_reject_blank_and_unknown_ticket(self):
        with self.assertRaises(ValueError):
            create_ticket(self.db, ' ', 'Office A')
        with self.assertRaises(LookupError):
            change_status(self.db, 99, 'resolved')

    def test_csv_export(self):
        create_ticket(self.db, 'Password reset', 'Employee', priority='low')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'export.csv'
            self.assertEqual(export_csv(self.db, path), 1)
            with path.open(newline='') as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]['title'], 'Password reset')


if __name__ == '__main__':
    unittest.main()
