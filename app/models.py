from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# users table
class User(db.Model, UserMixin):  # UserMixin is required for Flask-Login
    __tablename__ = "users"  # Corrected from "user" to "users"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password_hash = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)
    is_official = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    community_library = db.relationship("CommunityLibrary", backref="user_owner", lazy="select")
    messages_sent = db.relationship("Message", foreign_keys='Message.sender_id', backref="sender", lazy="select")
    messages_received = db.relationship("Message", foreign_keys='Message.receiver_id', backref="receiver", lazy="select")
    programs_created = db.relationship("Program", backref="creator", lazy="select")
    school_library_uploads = db.relationship("SchoolLibrary", backref="uploader", lazy="select")
    subscriptions = db.relationship("Subscription", backref="subscriber", lazy="select")
    student = db.relationship("Student", backref="student_user", uselist=False)
    teacher = db.relationship("Teacher", backref="teacher_user", uselist=False)

    # Password Methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.user_id)


# all of the following tables follow the same formatting as above

# community library table
class CommunityLibrary(db.Model):
    __tablename__ = "community_library"
    content_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)

# message table
class Message(db.Model):
    __tablename__ = "message"
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message_content = db.Column(db.String(500), nullable=False)
    sent_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

# program table
class Program(db.Model):
    __tablename__ = "program"
    program_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    program_name = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

# school table
class School(db.Model):
    __tablename__ = "school"
    school_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_name = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    contact_email = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)

# school library table
class SchoolLibrary(db.Model):
    __tablename__ = "school_library"
    school_library_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.Integer, db.ForeignKey("school.school_id"), nullable=False)
    title = db.Column(db.String(250), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

# student table
class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey("school.school_id"), nullable=False)
    submissions = db.relationship("StudentSubmission", backref="student", lazy="select")

# student teacher table
class StudentTeacher(db.Model):
    __tablename__ = "student_teacher"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.teacher_id"), nullable=False)
    assigned_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)

# student submission table
class StudentSubmission(db.Model):
    __tablename__ = "student_submission"
    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    submitted_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)

# subscription table
class Subscription(db.Model):
    __tablename__ = "subscription"
    subscription_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("program.program_id"), nullable=False)
    subscription_date = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)

# teacher table
class Teacher(db.Model):
    __tablename__ = "teacher"
    teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey("school.school_id"), nullable=False)
