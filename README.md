# Library Management System

A desktop app for college libraries. Manage books, students, borrow/return, and fines.

Built with Python + SQLite.

---

## Features

- Admin login with password hashing
- Add/edit/delete books and students
- Borrow/return books with due dates
- Auto fine calculation (₹5/day after 14 days)
- Search books and students
- Dashboard with stats
- Export reports to CSV/TXT
- Duplicate prevention (no same book/student twice)

---

## Tech Stack

- Python 3.7+
- SQLite3
- Tkinter

---

## How to Run

```bash
python main.py
```

**Default login:** admin / admin123

---

## Project Structure

```
├── core/
│   ├── db.py          # Database connection
│   ├── auth.py        # Login & password hashing
│   ├── books.py       # Book operations
│   ├── students.py    # Student operations
│   ├── borrow.py      # Borrow/return & fines
│   └── exporter.py    # CSV/TXT export
├── gui.py             # Main interface
├── main.py            # Start here
└── data/              # Database folder (auto created)
```

---

## What Works

- [x] Admin login with lockout after 3 attempts
- [x] Book CRUD with duplicate check
- [x] Student CRUD with duplicate check
- [x] Borrow/return with available copies tracking
- [x] Fine calculation
- [x] Search in all tabs
- [x] Reports with export

---

## What Doesn't (Yet)

- Email/SMS reminders
- Online reservations
- Barcode scanning
