
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length
from wtforms import TextAreaField, SubmitField, MultipleFileField, HiddenField
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms import SubmitField
from wtforms import ValidationError

def email_domain_check(form, field):
    allowed_domain = "coventry.ac.uk"
    if not field.data.lower().endswith(f"@{allowed_domain}"):
        raise ValidationError(f"Registration allowed only for @{allowed_domain} emails.")


class StudentRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), email_domain_check])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class TeacherRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), email_domain_check])
    full_name = StringField('Full Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')


class CommunityUserRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher'), ('community', 'Community')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AssignStudentForm(FlaskForm):
    student_id = SelectField('Select Student to Assign', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Student')

class CreateClassForm(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired()])
    submit = SubmitField('Create Class')

class RenameClassForm(FlaskForm):
    name = StringField('New Class Name', validators=[DataRequired()])
    submit = SubmitField('Rename')

class DeleteClassForm(FlaskForm):
    submit = SubmitField('Delete Class')

class PostForm(FlaskForm):
    content = TextAreaField('Message/Note', validators=[DataRequired()])
    attachments = MultipleFileField('Attach Files')
    submit = SubmitField('Post')

class DeletePostForm(FlaskForm):
    submit = SubmitField('Delete')

class AssignmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    attachments = MultipleFileField('Attach Files')
    submit = SubmitField('Save Assignment')

class UploadLibraryMaterialForm(FlaskForm):
    file = FileField('Upload Material', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'docx', 'ppt', 'pptx', 'txt', 'xlsx', 'zip', 'jpg', 'png', 'mp4'], 'Files only!')
    ])
    submit = SubmitField('Upload')

class SubmissionForm(FlaskForm):
    file = FileField('Upload Submission', validators=[FileAllowed(['pdf', 'docx', 'ppt', 'pptx', 'txt', 'zip', 'jpg', 'png', 'mp4'], 'Files only!')])
    submit = SubmitField('Submit')

class StudentSubmissionForm(FlaskForm):
    file = FileField('Submit your work', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'docx', 'ppt', 'pptx', 'txt', 'xlsx', 'zip', 'jpg', 'png', 'mp4'], 'Invalid file type!')
    ])
    submit = SubmitField('Upload')

class DeleteFileForm(FlaskForm):
    submit = SubmitField('Delete')

class Enable2FAForm(FlaskForm):
    token = StringField('Token', validators=[DataRequired(), Length(min=6, max=6)])
    action = HiddenField(default="enable_2fa")
    submit = SubmitField('Enable 2FA')

class Disable2FAForm(FlaskForm):
    action = HiddenField(default="disable_2fa")
    submit = SubmitField('Disable 2FA')