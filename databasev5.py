# importing flask,sql and datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# establishing connection
app = Flask(__name__)
# this code is used to connect specifically to the database named db on my local machine
# postgres:HashmiRF2925 should be replaced with the username and password used on each machine for now and in the future the username and password for AWS
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:HashmiRF2925@localhost/db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# users table
class User(db.Model):
    __tablename__ = "users"  # Changed 'user' to 'users' to avoid conflicts
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)  # Made change, default=datetime.now(timezone.utc) to default=db.func.now()
    is_official = db.Column(db.Boolean, nullable=False)

    # user relationships linking foreign keys to their original tables and their class
    community_library = db.relationship("CommunityLibrary", backref="user_owner", lazy="select")  # Set lazy="select" (default) but can be changed
    messages_sent = db.relationship("Message", foreign_keys='Message.sender_id', backref="sender", lazy="select")
    messages_received = db.relationship("Message", foreign_keys='Message.receiver_id', backref="receiver", lazy="select")
    programs_created = db.relationship("Program", backref="creator", lazy="select")
    school_library_uploads = db.relationship("SchoolLibrary", backref="uploader", lazy="select")
    subscriptions = db.relationship("Subscription", backref="subscriber", lazy="select")
    student = db.relationship("Student", backref="student_user", uselist=False)
    teacher = db.relationship("Teacher", backref="teacher_user", uselist=False)

# all of the following tables follow the same formatting as above

# community library table
class CommunityLibrary(db.Model):
    __tablename__ = "community_library"
    content_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)

# message table
class Message(db.Model):
    __tablename__ = "message"
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message_content = db.Column(db.String(500), nullable=False)
    sent_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)

# program table
class Program(db.Model):
    __tablename__ = "program"
    program_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    program_name = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)

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
    uploaded_by = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)

# student table
class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey("school.school_id"), nullable=False)
    student_code = db.Column(db.String(7), nullable=False, unique=True)
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
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("program.program_id"), nullable=False)
    subscription_date = db.Column(db.TIMESTAMP, default=db.func.now(), nullable=False)

# teacher table
class Teacher(db.Model):
    __tablename__ = "teacher"
    teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey("school.school_id"), nullable=False)

# main program
if __name__ == "__main__":
    with app.app_context():   # uses application context so objects accessed outside of request handling***
        db.create_all()   # creates all tables
        print("Tables created successfully!")   # confirmation message


# *** --> This is used because Flask required the application contect to access the database 'db' 
# THIS IS NECESSARY AT THIS POINT PLEASE DON'T REMOVE.
