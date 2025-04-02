from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Users table
class User(db.Model, UserMixin):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(250), nullable=False, unique=True, index=True)
    email = db.Column(db.String(250), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False, index=True)
    is_official = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    community_library = db.relationship("CommunityLibrary", backref="user_owner", lazy="select", cascade="all, delete")
    messages_sent = db.relationship("Message", foreign_keys='Message.sender_id', backref="sender", lazy="select", cascade="all, delete")
    messages_received = db.relationship("Message", foreign_keys='Message.receiver_id', backref="receiver", lazy="select", cascade="all, delete")
    programs_created = db.relationship("Program", backref="creator", lazy="select", cascade="all, delete")
    school_library_uploads = db.relationship("SchoolLibrary", backref="uploader", lazy="select", cascade="all, delete")
    subscriptions = db.relationship("Subscription", backref="subscriber", lazy="select", cascade="all, delete")
    student = db.relationship("Student", backref="student_user", uselist=False, cascade="all, delete")
    teacher = db.relationship("Teacher", backref="teacher_user", uselist=False, cascade="all, delete")

    # Password Methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.user_id

    def __repr__(self):
        return f"<User {self.username}>"

# Community Library table
class CommunityLibrary(db.Model):
    __tablename__ = "community_libraries"
    content_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False, index=True)

# Messages table
class Message(db.Model):
    __tablename__ = "messages"
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message_content = db.Column(db.String(500), nullable=False)
    sent_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    status = db.Column(db.Enum("sent", "delivered", "read", name="message_status"), default="sent")

# Programs table
class Program(db.Model):
    __tablename__ = "programs"
    program_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    program_name = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

# Schools table
class School(db.Model):
    __tablename__ = "schools"
    school_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_name = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    contact_email = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False, index=True)

# School Libraries table
class SchoolLibrary(db.Model):
    __tablename__ = "school_libraries"
    school_library_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.school_id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(250), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

# Students table
class Student(db.Model):
    __tablename__ = "students"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.school_id", ondelete="CASCADE"), nullable=False)
    submissions = db.relationship("StudentSubmission", backref="student", lazy="select", cascade="all, delete")

# Student-Teacher Relationships table
class StudentTeacher(db.Model):
    __tablename__ = "student_teacher"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False)
    assigned_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)
    __table_args__ = (db.UniqueConstraint('student_id', 'teacher_id', name='uq_student_teacher'),)

# Student Submissions table
class StudentSubmission(db.Model):
    __tablename__ = "student_submissions"
    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    submitted_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False, index=True)

# Subscriptions table
class Subscription(db.Model):
    __tablename__ = "subscriptions"
    subscription_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("programs.program_id", ondelete="CASCADE"), nullable=False)
    subscription_date = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False, index=True)

# Teachers table
class Teacher(db.Model):
    __tablename__ = "teachers"
    teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.school_id", ondelete="CASCADE"), nullable=False)
