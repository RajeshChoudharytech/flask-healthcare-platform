from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum

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
