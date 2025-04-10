import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf.csrf import generate_csrf
from app import db
from app.models import CommunityUser, Student, Teacher, Class, Post, Attachment, Assignment, Submission, Community, CommunityMembership, CommunityPost, CommunityLibraryFile
from app.forms.forms import (
    StudentRegistrationForm, TeacherRegistrationForm, CommunityUserRegistrationForm,
    LoginForm, AssignStudentForm, CreateClassForm, RenameClassForm, DeleteClassForm,
    PostForm, DeletePostForm, AssignmentForm, UploadLibraryMaterialForm, PostForm, DeletePostForm, DeleteFileForm, Enable2FAForm, Disable2FAForm
)

import random
from datetime import datetime
from uuid import uuid4
import pyotp
import qrcode
import io
import base64

routes = Blueprint('routes', __name__)

UPLOAD_FOLDER = "app/static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ASSIGNMENT_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'assignments')
os.makedirs(ASSIGNMENT_UPLOAD_FOLDER, exist_ok=True)

SUBMISSION_FOLDER = os.path.join("app", "static", "submissions")
os.makedirs(SUBMISSION_FOLDER, exist_ok=True)

COMMUNITY_FOLDER = os.path.join("app", "static", "community")
os.makedirs(COMMUNITY_FOLDER, exist_ok=True)


def generate_id():
    return ''.join(random.choices('0123456789', k=5))

def login_user(user, role):
    session['user_id'] = user.id
    session['role'] = role

def get_current_user():
    role = session.get('role')
    user_id = session.get('user_id')
    if not role or not user_id:
        return None

    if role == 'teacher':
        return Teacher.query.get(user_id)
    elif role == 'student':
        return Student.query.get(user_id)
    elif role == 'community':
        return CommunityUser.query.get(user_id)

    return None

@routes.route('/register')
def register_gateway():
    return render_template('register.html')

@routes.route('/register/student', methods=['GET', 'POST'])
def reg_student():
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        if Student.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('routes.reg_student'))

        student = Student(
            email=form.email.data,
            username=form.email.data.split('@')[0],
            password=generate_password_hash(form.password.data),
            student_id=generate_id(),
            profile_picture='default_student.png'
        )
        db.session.add(student)
        db.session.commit()
        flash('Student registered successfully!', 'success')
        return redirect(url_for('routes.login'))

    return render_template('reg_student.html', form=form)

@routes.route('/register/teacher', methods=['GET', 'POST'])
def reg_teacher():
    form = TeacherRegistrationForm()
    if form.validate_on_submit():
        if Teacher.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('routes.reg_teacher'))

        teacher = Teacher(
            email=form.email.data,
            full_name=form.full_name.data,
            password=generate_password_hash(form.password.data),
            teacher_id=generate_id(),
            profile_picture='default_teacher.png'
        )
        db.session.add(teacher)
        db.session.commit()
        flash('Teacher registered successfully!', 'success')
        return redirect(url_for('routes.login'))

    return render_template('reg_teacher.html', form=form)

@routes.route('/register/community', methods=['GET', 'POST'])
def reg_public_user():
    form = CommunityUserRegistrationForm()
    if form.validate_on_submit():
        if CommunityUser.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('routes.reg_public_user'))

        user = CommunityUser(
            email=form.email.data,
            username=form.username.data,
            password=generate_password_hash(form.password.data),
            profile_picture='default_community.png'
        )
        db.session.add(user)
        db.session.commit()
        flash('Community user registered successfully!', 'success')
        return redirect(url_for('routes.login'))

    return render_template('reg_public_user.html', form=form)

@routes.route('/')
@routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        role = form.role.data
        email = form.email.data
        password = form.password.data

        user = None
        if role == 'student':
            user = Student.query.filter_by(email=email).first()
        elif role == 'teacher':
            user = Teacher.query.filter_by(email=email).first()
        elif role == 'community':
            user = CommunityUser.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if getattr(user, 'two_factor_enabled', False):
                session['pending_2fa_user'] = user.id
                session['pending_2fa_role'] = role
                return redirect(url_for('routes.otp_verify'))

            login_user(user, role)
            flash('Login successful!', 'success')
            return redirect(url_for('routes.account_settings'))

        flash('Invalid credentials.', 'danger')
        return redirect(url_for('routes.login'))

    return render_template('login.html', form=form)

@routes.route('/otp-verify', methods=['GET', 'POST'])
def otp_verify():
    user_id = session.get('pending_2fa_user')
    role = session.get('pending_2fa_role')

    if not user_id or not role:
        flash('Session expired or invalid access.', 'danger')
        return redirect(url_for('routes.login'))

    # Load user
    user = None
    if role == 'teacher':
        user = Teacher.query.get(user_id)
    elif role == 'student':
        user = Student.query.get(user_id)
    elif role == 'community':
        user = CommunityUser.query.get(user_id)

    if not user or not user.two_factor_enabled or not user.otp_secret:
        flash('Invalid session or 2FA setup.', 'danger')
        return redirect(url_for('routes.login'))

    if request.method == 'POST':
        token = request.form.get('token')
        totp = pyotp.TOTP(user.otp_secret)

        if totp.verify(token):
            # Complete login
            login_user(user, role)
            session.pop('pending_2fa_user', None)
            session.pop('pending_2fa_role', None)
            flash('2FA verification successful!', 'success')
            return redirect(url_for('routes.account_settings'))
        else:
            flash('Invalid token. Please try again.', 'danger')

    return render_template('otp_verify.html', role=role)

@routes.route('/account-settings', methods=['GET', 'POST'])
def account_settings():
    if 'user_id' not in session or 'role' not in session:
        flash('You must log in to access this page.', 'warning')
        return redirect(url_for('routes.login'))

    user = get_current_user()
    enable_form = Enable2FAForm()
    disable_form = Disable2FAForm()

    if enable_form.validate_on_submit() and enable_form.action.data == 'enable_2fa':
        secret = session.get('temp_otp_secret')
        if secret and pyotp.TOTP(secret).verify(enable_form.token.data):
            user.otp_secret = secret
            user.two_factor_enabled = True
            db.session.commit()
            session.pop('temp_otp_secret', None)
            flash('2FA enabled successfully!', 'success')
            return redirect(url_for('routes.account_settings'))
        else:
            flash('Invalid token. Try again.', 'danger')

    elif disable_form.validate_on_submit() and disable_form.action.data == 'disable_2fa':
        user.otp_secret = None
        user.two_factor_enabled = False
        db.session.commit()
        flash('2FA disabled.', 'info')
        return redirect(url_for('routes.account_settings'))

    # Prepare QR if not enabled
    otp_uri = qr_data = None
    if not user.two_factor_enabled:
        otp_secret = session.get('temp_otp_secret')
        if not otp_secret:
            otp_secret = pyotp.random_base32()
            session['temp_otp_secret'] = otp_secret

        otp_uri = pyotp.TOTP(otp_secret).provisioning_uri(
            name=user.email, issuer_name="KomodoHub"
        )

        qr = qrcode.make(otp_uri)
        buf = io.BytesIO()
        qr.save(buf, format='PNG')
        qr_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template(
        'account_settings.html',
        user=user,
        role=session['role'],
        otp_uri=otp_uri,
        qr_data=qr_data,
        enable_form=enable_form,
        disable_form=disable_form
    )

@routes.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('routes.login'))

@routes.route('/teacher/students')
def teacher_students():
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    teacher = Teacher.query.get(session['user_id'])
    students = Student.query.join(Class).filter(Class.teacher_id == teacher.id).all()
    return render_template('teacher_students.html', students=students)

@routes.route('/teacher/classes/<int:class_id>/remove/<int:student_id>')
def remove_student(class_id, student_id):
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    class_obj = Class.query.get_or_404(class_id)
    student = Student.query.get_or_404(student_id)

    if class_obj.teacher_id != session['user_id'] or student.class_id != class_id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('routes.manage_class', class_id=class_id))

    student.class_id = None
    db.session.commit()
    flash('Student removed from class.', 'info')
    return redirect(url_for('routes.manage_class', class_id=class_id))


@routes.route('/teacher/classes', methods=['GET', 'POST'])
def teacher_classes():
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    teacher = Teacher.query.get(session['user_id'])
    form = CreateClassForm()

    if form.validate_on_submit():
        existing_class = Class.query.filter_by(name=form.name.data, teacher_id=teacher.id).first()
        if existing_class:
            flash('You already have a class with this name.', 'warning')
        else:
            new_class = Class(name=form.name.data, teacher_id=teacher.id)
            db.session.add(new_class)
            db.session.commit()
            flash('Class created!', 'success')
            return redirect(url_for('routes.teacher_classes'))

    return render_template('teacher_classes.html', teacher=teacher, form=form)

@routes.route('/teacher/classes/<int:class_id>', methods=['GET', 'POST'])
def manage_class(class_id):
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('routes.teacher_classes'))

    assign_form = AssignStudentForm()
    rename_form = RenameClassForm()
    delete_form = DeleteClassForm()

    unassigned_students = Student.query.filter_by(class_id=None).all()
    assign_form.student_id.choices = [(s.id, s.email) for s in unassigned_students]

    if rename_form.submit.data and rename_form.validate_on_submit():
        duplicate = Class.query.filter_by(name=rename_form.name.data, teacher_id=session['user_id']).first()
        if duplicate and duplicate.id != class_obj.id:
            flash('Another class with this name already exists.', 'warning')
        else:
            class_obj.name = rename_form.name.data
            db.session.commit()
            flash('Class renamed.', 'success')
            return redirect(url_for('routes.manage_class', class_id=class_id))

    if assign_form.submit.data and assign_form.validate_on_submit():
        student = Student.query.get(assign_form.student_id.data)
        if student:
            student.class_id = class_id
            db.session.commit()
            flash('Student assigned!', 'success')
            return redirect(url_for('routes.manage_class', class_id=class_id))

    assigned_students = class_obj.students
    return render_template(
        'class_detail.html',
        class_obj=class_obj,
        assigned_students=assigned_students,
        assign_form=assign_form,
        rename_form=rename_form,
        delete_form=delete_form
    )

@routes.route('/teacher/classes/<int:class_id>/delete', methods=['POST'])
def delete_class(class_id):
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    class_obj = Class.query.get_or_404(class_id)

    if class_obj.teacher_id != session['user_id']:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('routes.teacher_classes'))

    for student in class_obj.students:
        student.class_id = None

    for post in class_obj.posts:
        for attachment in post.attachments:
            filepath = os.path.join("app", "static", "uploads", attachment.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            db.session.delete(attachment) 
        db.session.delete(post)

    db.session.delete(class_obj)
    db.session.commit()

    flash('Class deleted with all associated posts, attachments, and students unassigned.', 'info')
    return redirect(url_for('routes.teacher_classes'))

@routes.route('/teacher/classes/<int:class_id>/forum', methods=['GET', 'POST'])
def class_forum(class_id):
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    teacher_id = session.get('user_id')
    if not teacher_id:
        flash("You must be logged in to post.", "danger")
        return redirect(url_for('routes.login'))

    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != teacher_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('routes.teacher_classes'))

    form = PostForm()
    delete_form = DeletePostForm()

    if form.validate_on_submit():
        post = Post(
            content=form.content.data,
            class_id=class_id,
            teacher_id=teacher_id
        )
        db.session.add(post)
        db.session.flush()

        for file in request.files.getlist('attachments'):
            if file.filename:
                filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                db.session.add(Attachment(filename=filename, post_id=post.id))

        db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('routes.class_forum', class_id=class_id))

    posts = Post.query.filter_by(class_id=class_id).order_by(Post.created_at.desc()).all()
    return render_template(
        'class_forum.html',
        class_obj=class_obj,
        posts=posts,
        form=form,
        delete_form=delete_form
    )

@routes.route('/teacher/classes/<int:class_id>/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(class_id, post_id):
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    post = Post.query.get_or_404(post_id)
    if post.teacher_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('routes.class_forum', class_id=class_id))

    form = PostForm(content=post.content)

    if form.validate_on_submit():
        post.content = form.content.data

        # Handle new uploaded attachments
        for file in request.files.getlist('attachments'):
            if file.filename:
                filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                db.session.add(Attachment(filename=filename, post_id=post.id))

        # Handle deleted attachments
        deleted_ids = request.form.getlist('delete_attachment')
        for att_id in deleted_ids:
            att = Attachment.query.get(int(att_id))
            if att and att.post_id == post.id:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, att.filename))
                except FileNotFoundError:
                    pass
                db.session.delete(att)

        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('routes.class_forum', class_id=class_id))

    return render_template('edit_post.html', form=form, post=post)

@routes.route('/teacher/classes/<int:class_id>/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(class_id, post_id):
    form = DeletePostForm()
    if not form.validate_on_submit():
        flash('Invalid or missing CSRF token.', 'danger')
        return redirect(url_for('routes.class_forum', class_id=class_id))
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    post = Post.query.get_or_404(post_id)

    # Ownership check
    if post.teacher_id != session['user_id']:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('routes.class_forum', class_id=class_id))

    # Delete attached files from disk
    for attachment in post.attachments:
        file_path = os.path.join(UPLOAD_FOLDER, attachment.filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: could not delete file {file_path}. Reason: {e}")

    # Delete post (cascade should delete attachments if relationship is set up correctly)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully.', 'info')
    return redirect(url_for('routes.class_forum', class_id=class_id))

@routes.route('/teacher/classes/<int:class_id>/assignments', methods=['GET', 'POST'])
def class_assignments(class_id):
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('routes.teacher_classes'))

    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(
            class_id=class_id,
            teacher_id=session['user_id'],
            title=form.title.data,
            description=form.description.data
        )
        db.session.add(assignment)
        db.session.flush()

        for file in request.files.getlist('attachments'):
            if file.filename:
                filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
                filepath = os.path.join(ASSIGNMENT_UPLOAD_FOLDER, filename)
                file.save(filepath)
                db.session.add(Attachment(filename=filename, assignment_id=assignment.id))

        db.session.commit()
        flash('Assignment created.', 'success')
        return redirect(url_for('routes.class_assignments', class_id=class_id))

    assignments = Assignment.query.filter_by(class_id=class_id).order_by(Assignment.created_at.desc()).all()
    return render_template('class_assignments.html', class_obj=class_obj, form=form, assignments=assignments)

@routes.route('/teacher/assignment/<int:assignment_id>/edit', methods=['GET', 'POST'])
def edit_assignment(assignment_id):
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('routes.teacher_classes'))

    form = AssignmentForm(obj=assignment)

    if form.validate_on_submit():
        assignment.title = form.title.data
        assignment.description = form.description.data
        db.session.commit()
        flash('Assignment updated.', 'success')
        return redirect(url_for('routes.class_assignments', class_id=assignment.class_id))

    return render_template('edit_assignment.html', form=form, assignment=assignment)

@routes.route('/teacher/assignment/<int:assignment_id>/delete', methods=['POST'])
def delete_assignment(assignment_id):
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.teacher_id != session['user_id']:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('routes.teacher_classes'))

    # Delete attached files
    for attachment in assignment.attachments:
        filepath = os.path.join('app', 'static', 'uploads', 'assignments', attachment.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        db.session.delete(attachment)

    db.session.delete(assignment)
    db.session.commit()
    flash('Assignment deleted.', 'info')
    return redirect(url_for('routes.class_assignments', class_id=assignment.class_id))

@routes.route('/teacher/assignment/<int:assignment_id>/submissions')
def view_submissions(assignment_id):
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    assignment = Assignment.query.get_or_404(assignment_id)

    if assignment.teacher_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('routes.teacher_classes'))

    submissions = Submission.query.filter_by(assignment_id=assignment.id).all()

    return render_template('view_submissions.html', assignment=assignment, submissions=submissions)


@routes.route('/teacher/programs')
def teacher_programs():
    if session.get('role') != 'teacher':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    resources_path = os.path.join('app', 'static', 'resources')
    try:
        resources = os.listdir(resources_path)
    except FileNotFoundError:
        resources = []

    return render_template('teacher_programs.html', resources=resources)

@routes.route('/library', methods=['GET', 'POST'])
def library():
    form = UploadLibraryMaterialForm()
    library_folder = os.path.join('app', 'static', 'library')
    os.makedirs(library_folder, exist_ok=True)

    # Upload Logic (Teachers only)
    if session.get('role') == 'teacher' and form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(library_folder, filename))
        flash('File uploaded successfully.', 'success')
        return redirect(url_for('routes.library'))

    # List files
    try:
        files = os.listdir(library_folder)
    except FileNotFoundError:
        files = []

    return render_template('library.html', files=files, form=form, role=session.get('role'))

@routes.route('/library/delete/<filename>', methods=['POST'])
def delete_library_file(filename):
    if session.get('role') != 'teacher':
        flash('Unauthorized', 'danger')
        return redirect(url_for('routes.library'))

    file_path = os.path.join('app', 'static', 'library', filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File deleted.', 'info')
    else:
        flash('File not found.', 'warning')

    return redirect(url_for('routes.library'))

@routes.route('/student/my-class/forum', methods=['GET', 'POST'])
def student_forum():
    if session.get('role') != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    student = Student.query.get_or_404(session['user_id'])
    if not student.class_id:
        flash('You are not assigned to any class.', 'warning')
        return redirect(url_for('routes.account_settings'))

    class_obj = Class.query.get_or_404(student.class_id)
    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            content=form.content.data,
            class_id=student.class_id,
            student_id=student.id
        )
        db.session.add(post)
        db.session.flush()

        for file in request.files.getlist('attachments'):
            if file.filename:
                filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                db.session.add(Attachment(filename=filename, post_id=post.id))

        db.session.commit()
        flash('Post added.', 'success')
        return redirect(url_for('routes.student_forum'))

    posts = Post.query.filter_by(class_id=student.class_id).order_by(Post.created_at.desc()).all()
    return render_template('class_forum.html', class_obj=class_obj, posts=posts, form=form)

@routes.route('/student/my-assignments', methods=['GET'])
def my_assignments():
    if session.get('role') != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    student = Student.query.get_or_404(session['user_id'])

    if not student.class_id:
        flash("You are not assigned to any class.", "warning")
        return redirect(url_for('routes.account_settings'))

    class_obj = Class.query.get_or_404(student.class_id)
    assignments = Assignment.query.filter_by(class_id=class_obj.id).order_by(Assignment.created_at.desc()).all()

    # Map assignments to submissions (if any)
    submission_map = {}
    for submission in student.submissions:
        submission_map[submission.assignment_id] = submission

    return render_template(
        'student_assignments.html',
        assignments=assignments,
        student=student,
        class_obj=class_obj,
        submission_map=submission_map
    )

@routes.route('/student/assignments/<int:assignment_id>/submit', methods=['POST'])
def upload_submission(assignment_id):
    if session.get('role') != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    student = Student.query.get_or_404(session['user_id'])

    file = request.files.get('file')
    if not file or not file.filename:
        flash('No file selected.', 'warning')
        return redirect(url_for('routes.my_assignments'))

    filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
    filepath = os.path.join(SUBMISSION_FOLDER, filename)
    file.save(filepath)

    submission = Submission(
        assignment_id=assignment_id,
        student_id=student.id,
        filename=filename
    )
    db.session.add(submission)
    db.session.commit()

    flash('Submission uploaded successfully.', 'success')
    return redirect(url_for('routes.my_assignments'))


@routes.route('/student/submissions/<int:submission_id>/delete', methods=['POST'])
def delete_submission(submission_id):
    if session.get('role') != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    submission = Submission.query.get_or_404(submission_id)

    if submission.student_id != session['user_id']:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('routes.my_assignments'))

    file_path = os.path.join('app', 'static', 'submissions', submission.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(submission)
    db.session.commit()
    flash('Submission deleted.', 'info')
    return redirect(url_for('routes.my_assignments'))

@routes.route('/community')
def community_home():
    if session.get('role') != 'community':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    user_id = session['user_id']
    joined_community_ids = {
        m.community_id for m in CommunityMembership.query.filter_by(user_id=user_id).all()
    }
    all_communities = Community.query.all()

    return render_template(
        'community_home.html',
        all_communities=all_communities,
        memberships=joined_community_ids
    )


@routes.route('/community/join/<int:community_id>')
def join_community(community_id):
    if session.get('role') != 'community':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    user_id = session['user_id']
    already_member = CommunityMembership.query.filter_by(user_id=user_id, community_id=community_id).first()
    if not already_member:
        membership = CommunityMembership(user_id=user_id, community_id=community_id)
        db.session.add(membership)
        db.session.commit()
        flash('Joined community.', 'success')
    else:
        flash('You are already a member of this community.', 'info')

    return redirect(url_for('routes.community_home'))


@routes.route('/community/leave/<int:community_id>')
def leave_community(community_id):
    if session.get('role') != 'community':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    user_id = session['user_id']
    membership = CommunityMembership.query.filter_by(user_id=user_id, community_id=community_id).first()
    if membership:
        db.session.delete(membership)
        db.session.commit()
        flash('Left community.', 'info')
    else:
        flash('You are not a member of this community.', 'warning')

    return redirect(url_for('routes.community_home'))

@routes.route('/community/<int:community_id>/forum', methods=['GET', 'POST'])
def community_forum(community_id):
    if session.get('role') != 'community':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    community = Community.query.get_or_404(community_id)
    user_id = session.get('user_id')

    # Check if user is a member
    is_member = CommunityMembership.query.filter_by(
        community_id=community_id,
        user_id=user_id
    ).first()

    if not is_member:
        flash('Join the community to participate in the forum.', 'warning')
        return redirect(url_for('routes.community_home'))

    form = PostForm()
    delete_form = DeletePostForm()

    if form.validate_on_submit():
        post = CommunityPost(
            content=form.content.data,
            user_id=user_id,
            community_id=community_id
        )
        db.session.add(post)
        db.session.commit()
        flash('Post added.', 'success')
        return redirect(url_for('routes.community_forum', community_id=community_id))

    posts = (
        db.session.query(CommunityPost, CommunityUser)
        .join(CommunityUser, CommunityUser.id == CommunityPost.user_id)
        .filter(CommunityPost.community_id == community_id)
        .order_by(CommunityPost.created_at.desc())
        .all()
)

    return render_template(
        'community_forum.html',
        community=community,
        posts=posts,
        form=form,
        delete_form=DeletePostForm(),  # ensure this exists
        user=CommunityUser.query.get(user_id)  # pass current community user
    )


@routes.route('/community/<int:community_id>/post/<int:post_id>/delete', methods=['POST'])
def delete_community_post(community_id, post_id):
    if session.get('role') != 'community':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    post = CommunityPost.query.get_or_404(post_id)

    if post.user_id != session['user_id']:
        flash("You can only delete your own posts.", "danger")
        return redirect(url_for('routes.community_forum', community_id=community_id))

    # Validate CSRF token
    form = DeletePostForm()
    if not form.validate_on_submit():
        flash("Invalid CSRF token.", "danger")
        return redirect(url_for('routes.community_forum', community_id=community_id))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('routes.community_forum', community_id=community_id))

@routes.route('/community/<int:community_id>/library', methods=['GET', 'POST'])
def community_library(community_id):
    if session.get('role') != 'community':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    user_id = session['user_id']

    # Check if user is a member of this community
    membership = CommunityMembership.query.filter_by(user_id=user_id, community_id=community_id).first()
    if not membership:
        flash("You must join this community to access the library.", "warning")
        return redirect(url_for('routes.community_home'))

    upload_form = UploadLibraryMaterialForm()
    delete_form = DeleteFileForm()

    if upload_form.validate_on_submit():
        file = upload_form.file.data
        if file and file.filename:
            filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
            filepath = os.path.join(COMMUNITY_FOLDER, filename)
            file.save(filepath)

            db.session.add(CommunityLibraryFile(
                filename=filename,
                user_id=user_id,
                community_id=community_id
            ))
            db.session.commit()
            flash('File uploaded successfully!', 'success')
            return redirect(request.url)

    # Show only files for this community
    files = (
        db.session.query(CommunityLibraryFile, CommunityUser)
        .join(CommunityUser, CommunityLibraryFile.user_id == CommunityUser.id)
        .filter(CommunityLibraryFile.community_id == community_id)
        .order_by(CommunityLibraryFile.uploaded_at.desc())
        .all()
    )

    return render_template(
        'community/library.html',
        files=files,
        role='community',
        form=upload_form,
        delete_form=delete_form,
        session_user_id=user_id,
        community_id=community_id
    )

@routes.route('/community/<int:community_id>/library/delete/<int:file_id>', methods=['POST'])
def delete_community_file(community_id, file_id):
    if session.get('role') != 'community':
        flash('Access denied.', 'danger')
        return redirect(url_for('routes.login'))

    form = DeleteFileForm()
    if not form.validate_on_submit():
        flash("Invalid CSRF token.", "danger")
        return redirect(url_for('routes.community_library', community_id=community_id))

    file = CommunityLibraryFile.query.get_or_404(file_id)

    # Validate ownership
    if file.user_id != session['user_id']:
        flash("You can only delete your own files.", "danger")
        return redirect(url_for('routes.community_library', community_id=community_id))

    file_path = os.path.join(COMMUNITY_FOLDER, file.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(file)
    db.session.commit()
    flash("File deleted.", "info")
    return redirect(url_for('routes.community_library', community_id=community_id))

