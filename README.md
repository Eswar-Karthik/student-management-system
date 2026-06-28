# EduManage — Student Management System

A modern, production-style **Student Management System** built with Flask, SQLite, Bootstrap 5, and Chart.js. Designed to look and feel like a real SaaS admin product (think Notion / Google Workspace / Linear).

![EduManage](static/img/preview.png)

## ✨ Features

- 🔐 **Role-based authentication** — Admin, Teacher, Student accounts with session handling and password hashing
- 🪟 **Glassmorphism login page** with animated gradient background
- 📊 **Premium dashboard** — animated counters, growth chart, attendance breakdown, course distribution, recent activity feed
- 👨‍🎓 **Full student CRUD** — photo, roll no, contact, guardian, blood group, fees, attendance %, CGPA
- 🧑‍🏫 **Teacher & course management** with subject assignment
- 🗓 **Attendance** — Present / Absent / Late / Leave with one-click bulk marking
- 📝 **Results & grading** — internal + external marks, auto percentage, grade, downloadable report card
- 💳 **Fees** — Paid / Pending / Partial with printable receipts
- 🔎 **Global search** by name, roll no, course, department, email
- 📤 **Export** — CSV and printable PDF reports
- 🌓 **Dark mode + Light mode** with persistent preference
- 📱 **Fully responsive** — sidebar collapses, mobile-first layout
- 🛟 **Activity log**, toast notifications, flash messages, error pages, DB backup

## 🧰 Technology Stack

| Layer    | Tech                                 |
|----------|--------------------------------------|
| Backend  | Python 3, Flask 3, Flask-SQLAlchemy  |
| Database | SQLite                               |
| Frontend | HTML5, CSS3, JS (ES6), Bootstrap 5   |
| Charts   | Chart.js                             |
| Icons    | Font Awesome 6                       |
| Auth     | Werkzeug password hashing + sessions |

## 🚀 Installation

```bash
# 1. Clone / extract the project
cd edumanage-sms

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python app.py
```

Open **http://localhost:5000** in your browser.

## 🔑 Demo Credentials

| Role    | Username  | Password     |
|---------|-----------|--------------|
| Admin   | `admin`   | `admin123`   |
| Teacher | `teacher` | `teacher123` |
| Student | `student` | `student123` |

## 📁 Folder Structure

```
edumanage-sms/
├── app.py                  # Flask routes & app factory
├── models.py               # SQLAlchemy models
├── seed.py                 # Default users + demo data
├── requirements.txt
├── README.md
├── instance/
│   └── edumanage.db        # Auto-created SQLite DB
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── img/
└── templates/
    ├── base.html, home.html, login.html, dashboard.html
    ├── students.html, student_form.html, student_profile.html
    ├── teachers.html, courses.html
    ├── attendance.html, results.html, fees.html, receipt.html
    ├── reports.html, print_report.html
    ├── profile.html, settings.html, users.html
    └── error.html
```

## 🖼 Screenshots

> Replace these with real screenshots after running locally.

- `screenshots/login.png` — Glassmorphism login
- `screenshots/dashboard.png` — Analytics dashboard
- `screenshots/students.png` — Students table with search
- `screenshots/profile.png` — Student profile
- `screenshots/attendance.png` — Mark attendance
- `screenshots/dark.png` — Dark mode

## 🌱 Future Scope

- Email/SMS notifications for fee due dates
- Online fee payment integration (Stripe / Razorpay)
- Timetable / class scheduling module
- Library and hostel management
- Parent login portal
- Mobile app (React Native)

## 📄 License

MIT License — free to use, modify, and ship.

---

Built with ❤️ for students and educators.
