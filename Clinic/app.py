# app.py

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
    UserMixin,
)
from models import db, User, Doctor, Patient, Appointment
from forms import (
    LoginForm,
    RegistrationForm,
    DoctorForm,
    AppointmentForm,
    EditDoctorForm,
    DeleteDoctorForm,  
    AddPatientForm,
    PatientAppointmentForm,
    SearchForm  # إضافة SearchForm
)
import os
from sqlalchemy import text
from datetime import timedelta
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/zasaa/Desktop/clinc/instance/clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'maser'

db.init_app(app)

with app.app_context():
    db.create_all()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # إعادة التوجيه إلى 'login' للمستخدمين غير المصرح لهم


def test_db_connection():
    try:
        # Check if database file exists
        db_path = 'C:/Users/zasaa/Desktop/clinc/instance/clinic.db'
        if not os.path.exists(db_path):
            print("Database file not found at:", db_path)
            print("Creating new database...")
            
        # Try to execute a simple query
        db.session.execute(text('SELECT 1'))
        print("Database connection successful!")
        print(f"Database location: {db_path}")
        return True
    except Exception as e:
        print("Database connection failed!")
        print(f"Error: {str(e)}")
        print("Exiting application...")
        exit(1)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()  # التأكد من إنشاء جميع الجداول
    test_db_connection()
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin_user = User(
            email='admin@clinic.com',
            password=generate_password_hash('adminpassword'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin account created successfully!")
    else:
        print("Admin account already exists.")

# Index Route
@app.route('/')
def home():
    return render_template('base.html')

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # البحث عن المستخدم بناءً على البريد الإلكتروني
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            
            # الحصول على اسم المستخدم بناءً على نوع المستخدم
            user_name = None
            if user.role == 'doctor':
                doctor = Doctor.query.filter_by(email=user.email).first()
                if doctor:
                    user_name = f"Dr. {doctor.first_name} {doctor.last_name}"
            elif user.role == 'patient':
                patient = Patient.query.filter_by(email=user.email).first()
                if patient:
                    user_name = f"{patient.first_name} {patient.last_name}"
            
            # تخزين اسم المستخدم في الجلسة
            if user_name:
                session['user_name'] = user_name
            
            flash('You have successfully logged in!', 'success')
            # إعادة التوجيه بناءً على الدور
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)

# Delete Patient Route
@app.route('/admin/delete_patient/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient_record(patient_id):
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('patients_list'))

    patient = Patient.query.get_or_404(patient_id)
    user = User.query.filter_by(email=patient.email, role='patient').first()

    try:
        if user:
            db.session.delete(user)
        db.session.delete(patient)
        db.session.commit()
        flash('Patient deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the patient.', 'danger')
        print(e)

    return redirect(url_for('patients_list'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email is already in use. Please use a different email.', 'warning')
            return redirect(url_for('register'))
        
        # Create hashed password once
        hashed_password = generate_password_hash(form.password.data)
        
        # Create new patient with hashed password
        new_patient = Patient(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            gender=form.gender.data,
            password=hashed_password
        )
        db.session.add(new_patient)
        
        # Create user account with same hashed password
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            role='patient'
        )
        db.session.add(new_user)
        
        try:
            db.session.commit()
            login_user(new_user)
            flash('Registered successfully!', 'success')
            return redirect(url_for('patient_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration.', 'danger')
            print(f"Error: {str(e)}")
            
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# Admin Routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))
    doctors_count = Doctor.query.count()
    patients_count = Patient.query.count()
    appointments_count = Appointment.query.count()
    recent_appointments = Appointment.query.options(
        db.joinedload(Appointment.patient_details),
        db.joinedload(Appointment.doctor_details)
    ).order_by(Appointment.date.desc()).limit(5).all()
    recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
    
    return render_template(
        'admin/admin_dashboard.html',
        doctors_count=doctors_count,
        patients_count=patients_count,
        appointments_count=appointments_count,
        recent_appointments=recent_appointments,
        recent_patients=recent_patients,
        current_year=datetime.now().year
    )

@app.route('/admin/doctors')
@login_required
def doctors_list():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))
    doctors = Doctor.query.all()
    form = DeleteDoctorForm()  # إنشاء نموذج الحذف
    return render_template('admin/doctors_list.html', doctors=doctors, form=form, current_year=datetime.now().year)

@app.route('/admin/patients')
@login_required
def patients_list():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))
    patients = Patient.query.all()
    return render_template('admin/patients_list.html', patients=patients, current_year=datetime.now().year)

@app.route('/admin/appointments')
@login_required
def appointments():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))
    appointments = Appointment.query.all()
    # جلب معلومات المريض لكل موعد
    for appointment in appointments:
        appointment.patient = db.session.get(Patient, appointment.patient_id)
        appointment.doctor = db.session.get(Doctor, appointment.doctor_id)

    return render_template('admin/appointments.html', appointments=appointments, current_year=datetime.now().year)

@app.route('/admin/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))
        
    form = DoctorForm()
    if form.validate_on_submit():
        try:
            # التحقق من وجود البريد الإلكتروني
            if Doctor.query.filter_by(email=form.email.data).first():
                flash('Email already exists!', 'danger')
                return render_template('admin/add_doctor.html', form=form)
                
            # إنشاء حساب الطبيب
            doctor = Doctor(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone_number=form.phone_number.data,
                password=generate_password_hash(form.password.data),
                consultation_fee=form.consultation_fee.data
            )
            
            # إنشاء حساب المستخدم للطبيب
            user = User(
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                role='doctor'
            )
            
            # حفظ في قاعدة البيانات
            db.session.add(doctor)
            db.session.add(user)
            db.session.commit()
            
            flash('Doctor added successfully!', 'success')
            return redirect(url_for('doctors_list'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error adding doctor. Please try again.', 'danger')
            print(f"Error: {str(e)}")
            
    return render_template('admin/add_doctor.html', form=form)

@app.route('/admin/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))

    form = AddPatientForm()
    if form.validate_on_submit():
        try:
            # التحقق من وجود البريد الإلكتروني
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('A user with this email already exists.', 'danger')
                return render_template('admin/add_patient.html', form=form)

            # إنشاء حساب المستخدم
            hashed_password = generate_password_hash(form.password.data)
            user = User(email=form.email.data, password=hashed_password, role='patient')
            db.session.add(user)
            db.session.flush()  # للحصول على user.id

            # إنشاء سجل المريض
            patient = Patient(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                gender=form.gender.data,
                phone_number=form.phone_number.data,
                email=form.email.data,
                password=hashed_password
            )
            db.session.add(patient)
            db.session.commit()
            flash('Patient added successfully!', 'success')
            return redirect(url_for('patients_list'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the patient.', 'danger')
            print(f"Error adding patient: {str(e)}")
            
    return render_template('admin/add_patient.html', form=form)

# Delete Appointment Route
@app.route('/admin/delete_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('appointments'))

    appointment = db.session.get(Appointment, appointment_id)
    if appointment is None:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('appointments'))
    
    try:
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting appointment: {str(e)}')
        flash('An error occurred while deleting the appointment.', 'danger')
    
    return redirect(url_for('appointments'))

@app.route('/admin/book_appointment', methods=['GET', 'POST'])
@login_required
def admin_book_appointment():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))

    form = AppointmentForm()
    
    # تحميل قائمة المرضى والأطباء
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    
    form.patient_id.choices = [(p.id, f"{p.first_name} {p.last_name}") for p in patients] if patients else []
    form.doctor_id.choices = [(d.id, f"Dr. {d.first_name} {d.last_name}") for d in doctors] if doctors else []
    
    if form.validate_on_submit():
        try:
            doctor = db.session.get(Doctor, form.doctor_id.data)
            patient = db.session.get(Patient, form.patient_id.data)
            
            if doctor and patient:
                # التحقق من عدم وجود موعد في نفس الوقت
                existing_appointment = Appointment.query.filter_by(
                    doctor_id=doctor.id,
                    date=form.date.data,
                    time=form.time.data
                ).first()
                
                if existing_appointment:
                    flash('This time slot is already booked. Please choose another time.', 'danger')
                    return render_template('admin/book_appointment.html', form=form)
                
                new_appointment = Appointment(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    date=form.date.data,
                    time=form.time.data,
                    fee=doctor.consultation_fee,
                    status='pending'
                )
                db.session.add(new_appointment)
                db.session.commit()
                flash('Appointment booked successfully!', 'success')
                return redirect(url_for('appointments'))
            else:
                flash('Selected doctor or patient not found.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while booking the appointment.', 'danger')
            print(f"Error booking appointment: {str(e)}")
    
    return render_template(
        'admin/book_appointment.html',
        form=form,
        current_year=datetime.now().year
    )

# تحديث حالة الموعد
@app.route('/admin/update_appointment_status/<int:appointment_id>', methods=['POST'])
@login_required
def update_appointment_status(appointment_id):
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('appointments'))

    appointment = db.session.get(Appointment, appointment_id)
    if appointment is None:
        flash('Date not found.', 'danger')
        return redirect(url_for('appointments'))
    
    new_status = request.form.get('status')
    if new_status not in ['pending', 'confirmed', 'cancelled', 'completed']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('appointments'))

    try:
        appointment.status = new_status
        db.session.commit()
        flash('Appointment status updated successfully.!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'خطأ في تحديث حالة الموعد: {str(e)}')
        flash('حدث خطأ أثناء تحديث حالة الموعد.', 'danger')
    
    return redirect(url_for('appointments'))

# Doctor Routes
@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))
    
    # جلب معلومات الطبيب والمواعيد
    doctor = Doctor.query.filter_by(email=current_user.email).first()
    if doctor:
        appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
        # إضافة معلومات المريض لكل موعد
        for appointment in appointments:
            appointment.patient = Patient.query.get(appointment.patient_id)
    else:
        appointments = []
        flash('Doctor profile not found.', 'danger')
    
    return render_template(
        'doctor/doctor_dashboard.html',
        appointments=appointments,
        doctor=doctor,
        current_year=datetime.now().year
    )

# Patient Routes
@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))
    patient = Patient.query.filter_by(email=current_user.email).first()
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    # جلب معلومات الطبيب لكل موعد
    for appointment in appointments:
        appointment.doctor = Doctor.query.get(appointment.doctor_id)
    return render_template(
        'patient/patient_dashboard.html',
        appointments=appointments,
        current_year=datetime.now().year,
        patient=patient
    )

@app.route('/patient/appointments')
@login_required
def patient_appointments():
    if current_user.role != 'patient':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))
    patient = Patient.query.filter_by(email=current_user.email).first()
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    return render_template(
        'patient/appointments.html',
        appointments=appointments,
        current_year=datetime.now().year
    )

@app.route('/patient/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if not current_user.is_authenticated or current_user.role != 'patient':
        return redirect(url_for('login'))

    # الحصول على معرف المريض من جدول المرضى
    patient = Patient.query.filter_by(email=current_user.email).first()
    if not patient:
        flash('Patient record not found.', 'danger')
        return redirect(url_for('login'))

    form = PatientAppointmentForm()
    
    # تحميل قائمة الأطباء
    doctors = Doctor.query.all()
    form.doctor_id.choices = [(d.id, f"Dr. {d.first_name} {d.last_name}") for d in doctors] if doctors else []
    
    if form.validate_on_submit():
        try:
            doctor = Doctor.query.get(form.doctor_id.data)
            if doctor:
                # التحقق من عدم وجود موعد في نفس الوقت
                existing_appointment = Appointment.query.filter_by(
                    doctor_id=doctor.id,
                    date=form.date.data,
                    time=form.time.data
                ).first()
                
                if existing_appointment:
                    flash('Sorry, this appointment is already booked. Please choose another time.', 'danger')
                    return render_template('patient/book_appointment.html', form=form)
                
                new_appointment = Appointment(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    date=form.date.data,
                    time=form.time.data,
                    fee=doctor.consultation_fee,
                    status='pending'
                )
                db.session.add(new_appointment)
                db.session.commit()
                flash('Appointment booked successfully!', 'success')
                return redirect(url_for('patient_dashboard'))
            else:
                flash('Selected doctor not found.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while booking the appointment.', 'danger')
            print(f"Error booking appointment: {str(e)}")
    
    return render_template(
        'patient/book_appointment.html',
        form=form,
        current_year=datetime.now().year
    )


# API Routes for JavaScript
@app.route('/get_doctor_fee/<int:doctor_id>')
@login_required
def get_doctor_fee(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return jsonify({'fee': doctor.consultation_fee})

# Delete Doctor Route
@app.route('/admin/delete_doctor/<int:doctor_id>', methods=['POST'])
@login_required
def delete_doctor(doctor_id):
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('doctors_list'))

    doctor = Doctor.query.get_or_404(doctor_id)
    user = User.query.filter_by(email=doctor.email, role='doctor').first()

    try:
        # حذف جميع المواعيد المرتبطة بالطبيب أولاً
        Appointment.query.filter_by(doctor_id=doctor_id).delete()
        
        # حذف حساب المستخدم المرتبط بالطبيب إذا وجد
        if user:
            db.session.delete(user)
            
        # حذف الطبيب
        db.session.delete(doctor)
        db.session.commit()
        flash('Doctor deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the doctor.', 'danger')
        print(f"Error deleting doctor: {str(e)}")

    return redirect(url_for('doctors_list'))

@app.route('/admin/clear_database', methods=['POST'])
@login_required
def clear_database():
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('admin_dashboard'))

    try:
        # مسح البيانات من الجداول
        db.session.execute("DELETE FROM patient")
        db.session.execute("DELETE FROM appointment")
        db.session.execute("DELETE FROM doctor")
        db.session.commit()
        flash('All data cleared successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while clearing the data.', 'danger')
        print("Error:", e)  # طباعة تفاصيل الخطأ هنا

    return redirect(url_for('admin_dashboard'))

# Edit Doctor Route
@app.route('/admin/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def edit_doctor(doctor_id):
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))
    
    doctor = Doctor.query.get_or_404(doctor_id)
    form = EditDoctorForm(obj=doctor)  # Fill form with current doctor data
    
    if form.validate_on_submit():
        # Update doctor details
        doctor.first_name = form.first_name.data
        doctor.last_name = form.last_name.data
        doctor.email = form.email.data
        doctor.phone_number = form.phone_number.data
        doctor.consultation_fee = form.consultation_fee.data
        doctor.password = form.password.data  # Store the password as plain text

        # Find or create corresponding user account for the doctor
        user = User.query.filter_by(email=doctor.email, role='doctor').first()
        if user:
            # Update user details
            user.email = form.email.data
            user.password = form.password.data  # Store the password as plain text
        else:
            # Create a new User account if it doesn't exist
            new_user = User(
                email=form.email.data,
                password=form.password.data,  # Store the password as plain text
                role='doctor'
            )
            db.session.add(new_user)
            flash('Associated user account created for the doctor.', 'info')
        
        try:
            db.session.commit()
            flash('Doctor information updated successfully!', 'success')
            return redirect(url_for('doctors_list'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the doctor.', 'danger')
            print(e)  # For debugging
    
    return render_template('admin/edit_doctor.html', form=form, doctor=doctor, current_year=datetime.now().year)

@app.route('/admin/search', methods=['GET', 'POST'])
@login_required
def admin_search():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))

    form = SearchForm()
    results = []
    search_performed = False
    search_type = None
    
    if form.validate_on_submit():
        search_performed = True
        search_type = form.search_type.data
        search_query = f"%{form.search_query.data}%"
        
        if search_type == 'doctor':
            results = Doctor.query.filter(
                db.or_(
                    Doctor.first_name.ilike(search_query),
                    Doctor.last_name.ilike(search_query),
                    Doctor.email.ilike(search_query),
                    Doctor.phone_number.ilike(search_query),
                )
            ).all()
        else:
            results = Patient.query.filter(
                db.or_(
                    Patient.first_name.ilike(search_query),
                    Patient.last_name.ilike(search_query),
                    Patient.email.ilike(search_query),
                    Patient.phone_number.ilike(search_query)
                )
            ).all()
    
    return render_template(
        'admin/search.html',
        form=form,
        results=results,
        search_performed=search_performed,
        search_type=search_type,
        current_year=datetime.now().year
    )

@app.route('/reset_database')
@login_required
def reset_database():
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('index'))
        
    try:
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        # Create admin user
        admin_user = User(
            email='admin@clinic.com',
            password=generate_password_hash('adminpassword'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        flash('Database reset successfully!', 'success')
    except Exception as e:
        flash(f'Error resetting database: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

    

if __name__ == '__main__':
    app.run(port=5000, debug=True)