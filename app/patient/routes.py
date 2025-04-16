from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import UserRole, User

from app.forms import AppointmentForm
from app.models import Appointment, AppointmentStatus

from app import db


patient_bp = Blueprint("patient", __name__)

@patient_bp.route('/appointments/book/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book_appointment_with_doctor(doctor_id):
    """
    Allow a patient to book an appointment with a specific doctor.
    """
    if current_user.role != UserRole.patient:
        return "Unauthorized", 403

    doctor = User.query.filter_by(id=doctor_id, role=UserRole.doctor).first_or_404()
    form = AppointmentForm()

    if form.validate_on_submit():
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor.id,
            appointment_time=form.appointment_time.data
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment requested successfully!', 'success')
        return redirect(url_for('doctor.doctor_list'))

    return render_template('patient/book_appointment.html', form=form, doctor=doctor)
