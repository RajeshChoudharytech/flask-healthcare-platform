from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user
from app import db
from app.models import User
from flask import Blueprint
from werkzeug.security import check_password_hash


auth_bp = Blueprint('auth', __name__)

# Registration route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email, role='Patient')  # Default role is Patient
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# Login route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('auth.profile'))

        flash('Invalid login credentials', 'danger')

    return render_template('auth/login.html')


# Logout route
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('auth.login'))
