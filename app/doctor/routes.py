from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models import UserRole, User

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/doctor/dashboard')
@login_required
def dashboard():
    """
    Displays the doctor's dashboard. The route is protected with the `login_required` decorator.
    If the logged-in user is not a doctor, it returns an unauthorized response (HTTP 403).
    """
    if current_user.role != UserRole.doctor:
        return "Unauthorized", 403
    return render_template('doctor/dashboard.html', doctor=current_user)


@doctor_bp.route('/doctors')
def doctor_list():
    """
    Displays a list of all doctors. It fetches all users with the role 'doctor' 
    and renders a template displaying their information.
    """
    doctors = User.query.filter_by(role=UserRole.doctor).all()
    return render_template('doctor/doctor_list.html', doctors=doctors)


@doctor_bp.route('/doctors/<int:doctor_id>')
def doctor_profile(doctor_id):
    """
    Displays a specific doctor's profile. It retrieves the doctor using the provided doctor_id.
    If the doctor is not found or is not a doctor, it aborts with a 404 error.
    """
    doctor = User.query.get_or_404(doctor_id)
    if doctor.role != UserRole.doctor:
        abort(404)
    return render_template('doctor/doctor_profile.html', doctor=doctor)
