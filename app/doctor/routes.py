from flask import Blueprint, render_template, abort, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import UserRole, User
from app.models import Appointment, AppointmentStatus
from app import db
from app.utils.email import send_email



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


@doctor_bp.route('/doctor/appointments')
@login_required
def view_appointments():
    """
    Display a list of all appointment requests for the currently logged-in doctor.
    """
    if current_user.role != UserRole.doctor:
        return "Unauthorized", 403

    appointments = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.created_at.desc()).all()
    return render_template('doctor/view_appointments.html', appointments=appointments)


@doctor_bp.route('/doctor/appointments/<int:appointment_id>/<action>')
@login_required
def handle_appointment(appointment_id, action):
    """
    Allow a doctor to accept or reject a specific appointment.

    """
    if current_user.role != UserRole.doctor:
        return "Unauthorized", 403

    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.doctor_id != current_user.id:
        return "Unauthorized", 403

    if action == 'accept':
        appointment.status = AppointmentStatus.accepted
    elif action == 'reject':
        appointment.status = AppointmentStatus.rejected

    db.session.commit()
    
    status_msg = 'accepted' if appointment.status == AppointmentStatus.accepted else 'rejected'

    send_email(
        subject=f'Appointment {status_msg.title()}',
        recipients=[appointment.patient.email],
        body=f'Your appointment with Dr. {appointment.doctor.username} on {appointment.appointment_time} has been {status_msg}.'
    )
    flash(f'Appointment {action}ed.', 'info')
    return redirect(url_for('doctor.view_appointments'))
