# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """Main users table - contains login information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, comment='User email')
    password = db.Column(db.String(128), nullable=False, comment='Password')
    role = db.Column(db.String(20), nullable=False, comment='User type: admin, doctor, patient')
    created_at = db.Column(db.DateTime, server_default=db.func.now(), comment='Account creation date')


class Doctor(db.Model):
    """Doctors table - contains doctor information"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='Doctor ID')
    first_name = db.Column(db.String(50), nullable=False, comment='First name')
    last_name = db.Column(db.String(50), nullable=False, comment='Last name')
    email = db.Column(db.String(120), unique=True, nullable=False, comment='Email address')
    phone_number = db.Column(db.String(20), nullable=False, comment='Phone number')
    password = db.Column(db.String(128), nullable=False, comment='Password')
    consultation_fee = db.Column(db.Float, nullable=False, comment='Consultation fee')
    created_at = db.Column(db.DateTime, server_default=db.func.now(), comment='Registration date')

    # Relationships
    appointments = db.relationship('Appointment', backref='doctor_details')


class Patient(db.Model):
    """Patients table - contains patient information"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False, comment='First name')
    last_name = db.Column(db.String(50), nullable=False, comment='Last name')
    email = db.Column(db.String(120), unique=True, nullable=False, comment='Email address')
    phone_number = db.Column(db.String(20), nullable=False, comment='Phone number')
    password = db.Column(db.String(128), nullable=False, comment='Password')
    gender = db.Column(db.String(10), nullable=False, comment='Gender')
    created_at = db.Column(db.DateTime, server_default=db.func.now(), comment='Registration date')

    # Relationships
    appointments = db.relationship('Appointment', backref='patient_details')


class Appointment(db.Model):
    """Appointments table - contains appointment information"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, comment='Patient ID')
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, comment='Doctor ID')
    date = db.Column(db.Date, nullable=False, comment='Appointment date')
    time = db.Column(db.Time, nullable=False, comment='Appointment time')
    fee = db.Column(db.Float, nullable=False, comment='Appointment fee')
    status = db.Column(db.String(20), default='pending', comment='Status: pending, confirmed, cancelled, completed')
    created_at = db.Column(db.DateTime, server_default=db.func.now(), comment='Creation date')
