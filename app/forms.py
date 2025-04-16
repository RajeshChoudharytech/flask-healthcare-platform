from wtforms.fields import DateField, TimeField
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


class AvailabilityForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    submit = SubmitField('Add Availability')
