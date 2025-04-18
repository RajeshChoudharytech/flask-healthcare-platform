from flask import (
    Blueprint,
    render_template,
    abort,
    flash,
    redirect,
    url_for,
    request,
)
from flask_login import login_required, current_user
from app.models import UserRole, User, DoctorProfile
from app.models import Appointment, AppointmentStatus, Availability
from app import db
from app.utils.email import send_email
from app.forms import AvailabilityForm
from datetime import date, datetime, timedelta
from sqlalchemy import func, desc


doctor_bp = Blueprint("doctor", __name__)


@doctor_bp.route("/doctor/dashboard")
@login_required
def dashboard():
    if current_user.role != UserRole.doctor:
        return "Unauthorized", 403

    today = date.today()

    total_patients = (
        db.session.query(Appointment.patient_id)
        .filter(Appointment.doctor_id == current_user.id)
        .distinct()
        .count()
    )

    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    todays_patients = (
        db.session.query(Appointment.patient_id)
        .filter(Appointment.doctor_id == current_user.id)
        .filter(Appointment.appointment_time >= start_of_day)
        .filter(Appointment.appointment_time <= end_of_day)
        .distinct()
        .count()
    )

    total_appointments = Appointment.query.filter_by(doctor_id=current_user.id).count()
    tomorrow = datetime.combine(date.today() + timedelta(days=1), datetime.min.time())

    upcoming_appointments = (
        Appointment.query
        .filter(
            Appointment.doctor_id == current_user.id,
            Appointment.appointment_time >= tomorrow
        )
        .order_by(desc(Appointment.appointment_time))
        .all()
    )

    todays_appointments = (
        Appointment.query.filter(
            Appointment.doctor_id == current_user.id,
            func.date(Appointment.appointment_time) == date.today(),
        )
        .order_by(desc(Appointment.appointment_time))
        .all()
    )

    section = request.args.get('section', 'upcoming')
    return render_template(
        "doctor/doctor-dashboard.html",
        doctor=current_user,
        total_patients=total_patients,
        todays_patients=todays_patients,
        total_appointments=total_appointments,
        today_date=today.strftime("%d, %b %Y"),
        upcoming_appointments=upcoming_appointments,
        todays_appointments=todays_appointments,
        active_section=section
    )


@doctor_bp.route("/doctors")
def doctor_list():
    """
    Displays a list of all doctors. It fetches all users with the role 'doctor'
    and renders a template displaying their information.
    """
    doctors = User.query.filter_by(role=UserRole.doctor).all()
    return render_template("doctor/doctor_list.html", doctors=doctors)


@doctor_bp.route("/doctors/<int:doctor_id>")
def doctor_profile(doctor_id):
    """
    Displays a specific doctor's profile. It retrieves the doctor using the provided doctor_id.
    If the doctor is not found or is not a doctor, it aborts with a 404 error.
    """
    doctor = User.query.get_or_404(doctor_id)
    if doctor.role != UserRole.doctor:
        abort(404)
    return render_template("doctor/doctor_profile.html", doctor=doctor)


@doctor_bp.route("/doctor/appointments/<int:appointment_id>/<action>")
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

    if action == "accept":
        appointment.status = AppointmentStatus.accepted
    elif action == "reject":
        appointment.status = AppointmentStatus.rejected

    db.session.commit()

    section = request.args.get('section', 'today')
    status_msg = (
        "accepted" if appointment.status == AppointmentStatus.accepted else "rejected"
    )

    send_email(
        subject=f"Appointment {status_msg.title()}",
        recipients=[appointment.patient.email],
        body=f"Your appointment with Dr. {appointment.doctor.username} on {appointment.appointment_time} has been {status_msg}.",
    )
    flash(f"Appointment {action}ed.", "info")
    return redirect(url_for("doctor.dashboard", section=section))


@doctor_bp.route("/doctor/availability", methods=["GET", "POST"])
@login_required
def manage_availability():
    """
    Allows a doctor to manage their availability for appointments.

    GET:
        Displays a form for the doctor to add new availability slots and lists all
        existing availability slots for the doctor.

    POST:
        When the form is submitted, validates the input, creates a new availability
        entry for the doctor, and saves it to the database.
    """
    if current_user.role != UserRole.doctor:
        abort(403)

    form = AvailabilityForm()
    if form.validate_on_submit():
        availability = Availability(
            doctor_id=current_user.id,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
        )
        db.session.add(availability)
        db.session.commit()
        flash("Availability added successfully.", "success")
        return redirect(url_for("doctor.manage_availability"))

    availabilities = (
        Availability.query.filter_by(doctor_id=current_user.id)
        .order_by(Availability.date.desc())
        .all()
    )
    return render_template(
        "doctor/schedule-timings.html", form=form, availabilities=availabilities
    )


@doctor_bp.route("/profile", methods=["GET", "POST"])
@login_required
def manage_profile():
    profile = DoctorProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        bio = request.form.get("bio")
        specialty = request.form.get("specialist")

        if not profile:
            profile = DoctorProfile(user_id=current_user.id)

        profile.bio = bio
        profile.specialty = specialty

        db.session.add(profile)
        db.session.commit()

        flash("Profile updated successfully!", "success")

    return render_template("doctor/doctor-profile-settings.html", profile=profile)


@doctor_bp.route('/doctor/appointments')
@login_required
def view_appointments():
    """
    Display a list of all appointment requests for the currently logged-in doctor.
    """
    if current_user.role != UserRole.doctor:
        return "Unauthorized", 403

    appointments = Appointment.query.filter_by(
        doctor_id=current_user.id,
        status=AppointmentStatus.pending
    ).order_by(Appointment.created_at.desc()).all()
    return render_template('doctor/appointments.html', appointments=appointments)


@doctor_bp.route('/doctor/patients')
@login_required
def view_patients():
    """
    Display a list of all patients for the currently logged-in doctor.
    """
    if current_user.role != UserRole.doctor:
        return "Unauthorized", 403

    patients = (
        User.query
        .join(Appointment, Appointment.patient_id == User.id)
        .filter(
            Appointment.doctor_id == current_user.id,
            User.role == UserRole.patient
        )
        .distinct()
        .all()
    )
    return render_template('doctor/my-patients.html', patients=patients)
