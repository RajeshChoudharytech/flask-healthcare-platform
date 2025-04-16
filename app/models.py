from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from datetime import datetime


class UserRole(enum.Enum):
    """
    Enum for User roles. It defines the different roles a user can have in the system.
    Possible roles: 'patient', 'doctor'.
    """
    patient = "patient"
    doctor = "doctor"


class User(UserMixin, db.Model):
    """
    User model representing a user in the system. It includes attributes for
    username, email, password hash, and role (either 'patient' or 'doctor').
    
    The model also includes a relationship to the 'DoctorProfile' model, which is 
    used for users with the 'doctor' role to store additional information about the doctor.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), nullable=False)

    # One-to-One: Only for doctors
    doctor_profile = db.relationship("DoctorProfile", back_populates="user", uselist=False)

    def set_password(self, password):
        """
        Sets the password for the user by hashing it using werkzeug's security utilities.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Checks if the given password matches the user's hashed password.
        """
        return check_password_hash(self.password_hash, password)


class DoctorProfile(db.Model):
    """
    DoctorProfile model representing additional information about a doctor.
    This model stores a doctor’s bio and specialty. It has a one-to-one relationship 
    with the User model, where each doctor is linked to a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    bio = db.Column(db.Text)
    specialty = db.Column(db.String(100))

    user = db.relationship("User", back_populates="doctor_profile")


class AppointmentStatus(enum.Enum):
    """
    Enum representing the status of an appointment.

    - 'Pending': The appointment is still waiting for confirmation.
    - 'Accepted': The appointment has been confirmed by the doctor.
    - 'Rejected': The appointment has been rejected by the doctor.
    """
    pending = "Pending"
    accepted = "Accepted"
    rejected = "Rejected"


class Appointment(db.Model):
    """
    Model representing an appointment between a patient and a doctor.

    Attributes:
        id (int): The unique identifier for the appointment.
        patient_id (int): The ID of the patient who booked the appointment.
        doctor_id (int): The ID of the doctor who will attend the appointment.
        appointment_time (datetime): The scheduled date and time of the appointment.
        status (str): The current status of the appointment (Pending, Accepted, Rejected).
        created_at (datetime): The timestamp when the appointment was created.
    """
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.pending)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_appointments')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_appointments')


class Availability(db.Model):
    """
    Represents a doctor's availability for appointments on a given date.

    Attributes:
        id (int): Primary key.
        doctor_id (int): Foreign key referencing the User table (must be a doctor).
        date (date): The specific date the doctor is available.
        start_time (time): The start time of the availability window.
        end_time (time): The end time of the availability window.
    """
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    doctor = db.relationship('User', backref='availabilities')
