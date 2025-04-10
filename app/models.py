from app import db

# --- Association Table (MUST be outside model classes) ---
user_community = db.Table('user_community',
    db.Column('user_id', db.Integer, db.ForeignKey('community_user.id')),
    db.Column('community_id', db.Integer, db.ForeignKey('community.id'))
)

# --- Users ---
class CommunityUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_picture = db.Column(db.String(300), nullable=True)
    posts = db.relationship('CommunityPost', backref='author', cascade="all, delete-orphan")
    otp_secret = db.Column(db.String(32), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    teacher_id = db.Column(db.String(5), unique=True, nullable=False)
    profile_picture = db.Column(db.String(300), nullable=False)
    otp_secret = db.Column(db.String(32), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('name', 'teacher_id', name='uix_class_name_teacher'),)

    teacher = db.relationship('Teacher', backref=db.backref('classes', lazy=True))
    students = db.relationship('Student', backref='class_', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    student_id = db.Column(db.String(5), unique=True, nullable=False)
    profile_picture = db.Column(db.String(300), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)
    otp_secret = db.Column(db.String(32), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    attachments = db.relationship('Attachment', backref='post', lazy=True)
    classroom = db.relationship('Class', backref='posts')
    teacher = db.relationship('Teacher', backref='posts')
    student = db.relationship('Student', backref='posts')

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id', name='fk_attachment_assignment_id'), nullable=True)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    attachments = db.relationship('Attachment', backref='assignment', lazy=True)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=True)
    filename = db.Column(db.String(300), nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())

    student = db.relationship('Student', backref='submissions')
    assignment = db.relationship('Assignment', backref='submissions')

# --- Communities ---
class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

class CommunityMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('community_user.id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), nullable=False)

class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('community_user.id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), nullable=False)

class CommunityLibraryFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('community_user.id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'), nullable=False)

