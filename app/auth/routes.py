from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user
from app import db
from app.models import User, UserRole
from flask import Blueprint
from werkzeug.security import check_password_hash


auth_bp = Blueprint('auth', __name__)

# Registration route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles the user registration process. When the user accesses the route
    via GET, the registration form is displayed. On POST, the submitted form data 
    (username, email, password, role) is processed to create a new user if the 
    email is not already in use. After successful registration, the user is redirected 
    to the login page.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# Login route

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles the login process. On GET request, it displays the login form.
    On POST request, it checks the credentials against the database and logs 
    the user in if valid. Depending on the user's role (doctor or patient), 
    the user is redirected to their appropriate dashboard.

    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')

            if user.role == UserRole.doctor:
                return redirect(url_for('doctor.dashboard'))
            elif user.role == UserRole.patient:
                return redirect(url_for('doctor.doctor_list'))
        flash('Invalid credentials.', 'danger')

    return render_template('auth/login.html')


# Logout route
@auth_bp.route('/logout')
@login_required
def logout():
    """
    Logs the user out of the session and redirects them to the login page.
    A flash message is shown confirming the logout.

    """
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('auth.login'))
