from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import UserRole, User, Availability
from app.utils.email import send_email

from app.forms import AppointmentForm
from app.models import Appointment

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
        selected_datetime = form.appointment_time.data
        selected_date = selected_datetime.date()
        selected_time = selected_datetime.time()

        # Fetch availability for this doctor on the selected date
        availability_slots = Availability.query.filter_by(doctor_id=doctor.id, date=selected_date).all()

        # Check if selected time falls within any availability slot
        is_available = any(slot.start_time <= selected_time <= slot.end_time for slot in availability_slots)

        if not is_available:
            flash("Selected time is outside the doctor's availability. Please choose another time.", "danger")
            return render_template('patient/book_appointment.html', form=form, doctor=doctor)

        # Proceed with booking
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor.id,
            appointment_time=selected_datetime
        )
        db.session.add(appointment)
        db.session.commit()

        send_email(
            subject='New Appointment Request',
            recipients=[doctor.email],
            body=f'You have a new appointment request from {current_user.username} on {form.appointment_time.data}.'
        )

        flash('Appointment requested successfully!', 'success')
        return redirect(url_for('doctor.doctor_list'))

    return render_template('patient/book_appointment.html', form=form, doctor=doctor)
