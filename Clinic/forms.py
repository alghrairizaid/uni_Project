# forms.py
# Forms for the Clinic Management System

from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    PasswordField, 
    SubmitField, 
    SelectField, 
    DecimalField, 
    DateField, 
    TimeField, 
    HiddenField
)
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError

def validate_phone(form, field):
    """Validate phone number to ensure it contains only digits"""
    if not field.data.isdigit():
        raise ValidationError('Phone number must contain only digits')
    if len(field.data) < 10 or len(field.data) > 15:
        raise ValidationError('Phone number must be between 10 and 15 digits')

class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """Form for patient registration"""
    first_name = StringField(
        'First Name',
        validators=[
            DataRequired(),
            Length(max=50)
        ]
    )
    last_name = StringField(
        'Last Name',
        validators=[
            DataRequired(),
            Length(max=50)
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )
    phone_number = StringField(
        'Phone Number',
        validators=[
            DataRequired(),
            Length(max=20),
            validate_phone
        ]
    )
    gender = SelectField(
        'Gender',
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other')
        ],
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )
    submit = SubmitField('Register')

class DoctorForm(FlaskForm):
    """Form for adding new doctors"""
    first_name = StringField(
        'First Name',
        validators=[
            DataRequired(),
            Length(max=50)
        ]
    )
    last_name = StringField(
        'Last Name',
        validators=[
            DataRequired(),
            Length(max=50)
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )
    phone_number = StringField(
        'Phone Number',
        validators=[
            DataRequired(),
            Length(max=20),
            validate_phone
        ]
    )
    consultation_fee = DecimalField(
        'Consultation Fee',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )
    submit = SubmitField('Add Doctor')

class EditDoctorForm(FlaskForm):
    """Form for editing doctor information"""
    first_name = StringField(
        'First Name',
        validators=[
            DataRequired(),
            Length(max=50)
        ]
    )
    last_name = StringField(
        'Last Name',
        validators=[
            DataRequired(),
            Length(max=50)
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )
    phone_number = StringField(
        'Phone Number',
        validators=[
            DataRequired(),
            Length(max=20),
            validate_phone
        ]
    )
    consultation_fee = DecimalField(
        'Consultation Fee',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password (Leave blank to keep current password)',
        validators=[
            Optional(),
            Length(min=6)
        ]
    )
    submit = SubmitField('Update Doctor')

class DeleteDoctorForm(FlaskForm):
    """Form for doctor deletion"""
    submit = SubmitField('Delete Doctor')

class AppointmentForm(FlaskForm):
    """نموذج حجز المواعيد"""
    patient_id = SelectField(
        'Patient',
        validators=[DataRequired()],
        coerce=int,
        default=None
    )
    doctor_id = SelectField(
        'Doctor',
        validators=[DataRequired()],
        coerce=int,
        default=None
    )
    date = DateField(
        'Date',
        validators=[DataRequired()],
        format='%Y-%m-%d'
    )
    time = TimeField(
        'Time',
        validators=[DataRequired()],
        format='%H:%M'
    )
    submit = SubmitField('Book Appointment')

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.patient_id.choices = []
        self.doctor_id.choices = []

class PatientAppointmentForm(FlaskForm):
    """نموذج حجز المواعيد للمرضى"""
    doctor_id = SelectField(
        'Doctor',
        validators=[DataRequired()],
        coerce=int
    )
    date = DateField(
        'Date',
        validators=[DataRequired()],
        format='%Y-%m-%d'
    )
    time = TimeField(
        'Time',
        validators=[DataRequired()],
        format='%H:%M'
    )
    submit = SubmitField('Book Appointment')

class AddPatientForm(FlaskForm):
    """نموذج لإضافة مريض جديد"""
    first_name = StringField(
        'First Name',
        validators=[
            DataRequired(),
            Length(max=50)
        ]
    )
    last_name = StringField(
        'Last Name',
        validators=[
            DataRequired(),
            Length(max=50)
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )
    phone_number = StringField(
        'Phone Number',
        validators=[
            DataRequired(),
            Length(max=20),
            validate_phone
        ]
    )
    gender = SelectField(
        'Gender',
        choices=[('Male', 'Male'), ('Female', 'Female')],
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )
    submit = SubmitField('Add Patient')

class SearchForm(FlaskForm):
    search_query = StringField('Search word', validators=[DataRequired()])
    search_type = SelectField('Search type', choices=[
        ('doctor', 'Doctor'),
        ('patient', 'Patient')
    ], validators=[DataRequired()])
    submit = SubmitField('Search')
