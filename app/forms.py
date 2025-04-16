from flask_wtf import FlaskForm
from wtforms import  SubmitField
from wtforms.validators import DataRequired
from wtforms.fields import DateTimeLocalField


class AppointmentForm(FlaskForm):
    appointment_time = DateTimeLocalField(
        'Preferred Time',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()],
        render_kw={"type": "datetime-local"}
    )
    submit = SubmitField('Book Appointment')