# IIPS Internship Management System

**IIPS Internship Record Management & Industry Collaboration System**

A web-based internship management system developed for IIPS to manage student internships, companies, mentors, evaluations, offers, and internship-related records in one place.

## Features

### Student Module

* Student registration and login
* Internship registration
* View internship details and status
* Browse available companies
* View internship offers
* View mentor evaluations

### Mentor Module

* Mentor login
* View assigned students
* View student internship details
* Evaluate assigned students
* Submit technical, communication, professionalism, and overall evaluations

### Admin Module

* Admin dashboard
* View internship statistics
* Company management
* Internship management
* Student management
* Offer management
* Internship analytics

### Internship Status Tracking

Internship status is automatically maintained according to the internship dates:

* **Pending** – Internship has not started
* **Ongoing** – Internship is currently in progress
* **Completed** – Internship end date has passed

## Technology Stack

* **Frontend:** HTML, CSS, Jinja2
* **Backend:** Python, Flask
* **Database:** SQLite
* **ORM:** Flask-SQLAlchemy
* **Authentication:** Flask-Login

## Project Structure

```text
IIPS-INTERNSHIP-MANAGEMENT-SYSTEM/
│
├── instance/
│   └── internship_system.db
│
├── static/
│   ├── css/
│   ├── images/
│   └── js/
│
├── templates/
│   ├── admin_dashboard.html
│   ├── analytics.html
│   ├── auth_base.html
│   ├── base.html
│   ├── company_database.html
│   ├── company_management.html
│   ├── internship_management.html
│   ├── intrnship_registration.html
│   ├── login.html
│   ├── mentor_dashboard.html
│   ├── my_evalaution.html
│   ├── my_internship.html
│   ├── my_students.html
│   ├── offer_management.html
│   ├── offer_tracking.html
│   ├── register.html
│   ├── student_dashboard.html
│   ├── student_evaluation.html
│   └── student_management.html
│
├── app.py
├── .gitignore
└── README.md
```

## How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/Asthap21/IIPS-Internship-Management-System.git
```

### 2. Open the project folder

```bash
cd IIPS-Internship-Management-System
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install the required packages

```bash
pip install flask flask-sqlalchemy flask-login
```

### 6. Run the application

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000/
```

## User Roles

The system supports three main roles:

* **Student** – Manages internship registration, companies, offers, and evaluations
* **Mentor** – Manages assigned students and their evaluations
* **Admin** – Manages students, companies, internships, offers, and analytics

## Database

The project uses SQLite for data storage. The local database is maintained inside the `instance/` directory.

The database directory is excluded from Git version control through `.gitignore` to prevent local database files from being committed.

## Purpose

The system is designed to simplify internship record management and improve coordination between students, mentors, administrators, and industry partners.

---

**Developed as an academic project for IIPS, DAVV, Indore.**
