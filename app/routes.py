from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.models import User, Student, Teacher
from app.forms import LoginForm, StudentRegisterForm, TeacherRegisterForm, UserRegisterForm
import os

# Home Route (Requires Login)
@app.route('/')
@login_required
def home():
    return render_template('home.html', user=current_user)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):  # Secure login check
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# General Registration Page (User Chooses Role)
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

# Public User Registration Route
@app.route('/register/public', methods=['GET', 'POST'])
def reg_public_user():
    form = UserRegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already exists. Please log in.', 'danger')
            return redirect(url_for('login'))

        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)  # Hash password before saving
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('reg_public_user.html', form=form)

# Student Registration Route
@app.route('/register/student', methods=['GET', 'POST'])
def reg_student():
    form = StudentRegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already exists. Please log in.', 'danger')
            return redirect(url_for('login'))

        # Create User account
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        # Create Student account linked to User
        new_student = Student(user_id=new_user.user_id, grade=form.grade.data, school_id=form.school_id.data)
        db.session.add(new_student)
        db.session.commit()

        flash('Student account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reg_student.html', form=form)

# Teacher Registration Route
@app.route('/register/teacher', methods=['GET', 'POST'])
def reg_teacher():
    form = TeacherRegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already exists. Please log in.', 'danger')
            return redirect(url_for('login'))

        # Create User account
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        # Create Teacher account linked to User
        new_teacher = Teacher(user_id=new_user.user_id, school_id=form.school_id.data)
        db.session.add(new_teacher)
        db.session.commit()

        flash('Teacher account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reg_teacher.html', form=form)

# Debug Mode Template Viewer
def get_template_files():
    template_dir = os.path.join(app.root_path, 'templates')
    templates = []
    for root, _, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                rel_path = os.path.relpath(os.path.join(root, file), template_dir)
                templates.append(rel_path.replace('\\', '/'))  # Normalize paths for Flask
    return templates

if app.debug:  # Only enable this in debug mode
    @app.route('/papafrita')
    def index():
        templates = get_template_files()
        return render_template('index.html', templates=templates)

    @app.route('/view/<path:template_name>')
    def view_template(template_name):
        return render_template(template_name)
