# Clinic Management System

A web-based clinic management system built with Flask that helps manage doctors, patients, and appointments.

## Features

### User Roles

- **Admin**
  - Manage doctors and patients
  - View and manage all appointments
  - Search functionality
  - Dashboard with statistics

- **Doctors**
  - View their appointments
  - Track consultation schedules

- **Patients**
  - Book appointments
  - View appointment history
  - Update personal information

### Core Functionality

- User authentication and authorization
- Appointment scheduling and management
- Patient records management
- Doctor profile management
- Consultation fee tracking

## Technical Stack

- **Backend**: Python/Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome

## Project Structure
```
clinic/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── admin/
│   ├── doctor/
│   ├── patient/
│   ├── auth/
│   └── shared/
├── models/
│   ├── user.py
│   ├── doctor.py
│   ├── patient.py
│   └── appointment.py
├── routes/
│   ├── admin.py
│   ├── doctor.py
│   ├── patient.py
│   └── auth.py
├── utils/
│   ├── helpers.py
│   └── decorators.py
├── config.py
├── requirements.txt
└── run.py
```

The project follows a modular structure:
- `static/`: Contains all static files (CSS, JavaScript, images)
- `templates/`: HTML templates organized by user roles
- `models/`: Database models and schema definitions
- `routes/`: Route handlers and business logic
- `utils/`: Helper functions and custom decorators
- `config.py`: Application configuration
- `run.py`: Application entry point

## Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/clinic-management.git
cd clinic-management
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Running the Application

1. Set environment variables:
- Windows:
```bash
set FLASK_APP=run.py
set FLASK_ENV=development
```
- Unix/MacOS:
```bash
export FLASK_APP=run.py
export FLASK_ENV=development
```

2. Start the development server:
```bash
flask run
```

3. Access the application at `http://localhost:5000`

## Default Admin Access
- Username: admin@clinic.com
- Password: admin123
