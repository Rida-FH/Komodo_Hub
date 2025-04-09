from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static', 'library')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'

users = {
    'student': {
        'username': 'student_user',
        'email': 'student@email.com',
        'join_date': '2023-10-01',
        'user_type': 'student',
        'class': 'Class 1'  # ← aquí defines a qué clase pertenece
    },
    'normal': {
        'username': 'regular_user',
        'email': 'regular@email.com',
        'join_date': '2023-10-01',
        'user_type': 'normal'
    },
    'teacher': {
        'username': 'teacher_user',
        'email': 'teacher@email.com',
        'join_date': '2023-10-01',
        'user_type': 'teacher'
    }
}


assignments = []
messages = []
classes = ["Class 1", "Class 2", "Class 3"]
class_forums = {cls: [] for cls in classes}

# ------------------ LOGIN ------------------

@app.route('/login/<user_type>')
def login_with_type(user_type):
    if user_type in users:
        session['user_type'] = user_type
        session['username'] = users[user_type]['username']
        return redirect(url_for('home'))
    else:
        return "Invalid user type", 404

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    user_type = session.get('user_type', 'student')
    if 'joined_communities' not in session:
        session['joined_communities'] = []
    if user_type == 'student':
        return redirect(url_for('home_student'))
    elif user_type == 'teacher':
        return redirect(url_for('home_teacher'))
    elif user_type == 'normal':
        return redirect(url_for('community_home'))

# ------------------ TEACHER CLASS FORUM ------------------

@app.route('/class_forum/<class_name>', methods=['GET', 'POST'])
def class_forum(class_name):
    if class_name not in classes:
        flash("Class not found")
        return redirect(url_for('home_teacher'))

    if request.method == 'POST':
        username = session.get('username', 'anonymous')
        message = request.form.get('message')
        image = request.files.get('image')

        post = {
            'username': username,
            'text': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'image_filename': None
        }

        if image and image.filename:
            filename = secure_filename(image.filename)
            folder = os.path.join("static", "forum_images")
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, filename)
            image.save(path)
            post['image_filename'] = f"forum_images/{filename}"

        class_forums[class_name].append(post)  # 👈 Aquí es donde se guarda el mensaje

    return render_template('class_forum.html',
                           user_type='teacher',
                           classes=classes,
                           current_class=class_name,
                           forum_messages=class_forums[class_name])  # 👈 Muestra mensajes de esa clase

# ------------------ ACCOUNT ------------------

@app.route('/account')
def account():
    user_type = session.get('user_type', 'student')
    user = users.get(user_type, {})
    return render_template('account.html', username=user.get('username'), email=user.get('email'), user_type=user_type)

@app.route('/change_password', methods=['POST'])
def change_password():
    new = request.form.get('new_password')
    confirm = request.form.get('confirm_password')
    if new != confirm:
        flash('Passwords do not match')
    else:
        flash('Password changed!')
    return redirect(url_for('account'))

@app.route('/update_profile_picture', methods=['POST'])
def update_profile_picture():
    file = request.files.get('profile_picture')
    if file and file.filename:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        flash('Profile picture updated')
    return redirect(url_for('account'))

@app.route('/update_username', methods=['POST'])
def update_username():
    new_name = request.form.get('new_username')
    user_type = session.get('user_type')
    if new_name:
        users[user_type]['username'] = new_name
        session['username'] = new_name
        flash('Username updated')
    return redirect(url_for('account'))

# ------------------ LIBRARY ------------------

@app.route('/library')
def student_library():  # Student library route
    user_type = session.get('user_type')
    if user_type != 'student':
        return redirect(url_for('home'))
    path = os.path.join(app.static_folder, 'library')
    files = [{'name': f, 'is_folder': os.path.isdir(os.path.join(path, f))} for f in os.listdir(path)]
    return render_template('library.html', files=files, user_type=user_type)

@app.route('/library_teacher')
def library_teacher():
    user_type = session.get('user_type')
    if user_type != 'teacher':
        return redirect(url_for('home'))

    path = os.path.join(app.static_folder, 'library')
    files = [{'name': f, 'is_folder': os.path.isdir(os.path.join(path, f))} for f in os.listdir(path)]
    return render_template('library_teacher.html', files=files, user_type=user_type)

UPLOAD_FOLDER = os.path.join('static', 'library')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if the directory exists, and if not, create it
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# This route is for community file uploads
# This route is for teacher file uploads
@app.route('/upload_teacher_file', methods=['POST'])
def upload_teacher_file():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure the target directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the file
        file.save(file_path)
        flash("File uploaded successfully.")
    return redirect(url_for('library_teacher'))


# ------------------ COMMUNITY LIBRARY ------------------

@app.route('/community_library/<community>')
def community_library(community):
    folder = os.path.join('static', 'community_library', community)
    os.makedirs(folder, exist_ok=True)
    files = os.listdir(folder)
    return render_template(
        'community_library.html',
        files=files,
        community=community,
        user_type='normal'
    )

@app.route('/upload_community_file', methods=['POST'])
def upload_community_file():
    if session.get('user_type') != 'normal':
        return redirect(url_for('home'))

    community = request.form.get('community')
    file = request.files.get('file')

    if file and file.filename and community:
        filename = secure_filename(file.filename)
        folder = os.path.join('static', 'community_library', community)
        os.makedirs(folder, exist_ok=True)
        file.save(os.path.join(folder, filename))
        flash("File uploaded successfully.")

    return redirect(url_for('community_library', community=community))




@app.route('/delete_file', methods=['POST'])
def delete_file():
    user_type = session.get('user_type', 'student')
    if user_type != 'teacher':
        flash('Only teachers can delete files.')
        return redirect(url_for('home'))

    filename = request.form.get('filename')
    if not filename:
        flash('No file specified.')
        return redirect(url_for('library_teacher'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            flash(f"Deleted: {filename}")
        else:
            flash('File does not exist or is not a file.')
    except Exception as e:
        flash(f"Error deleting file: {str(e)}")

    return redirect(url_for('library_teacher'))
@app.route('/download_community_file/<filename>')
def download_community_file(filename):
    # Asegurarse de que la ruta de la librería esté bien definida
    community_library_path = os.path.join('static', 'community_library')
    
    # El método send_from_directory se encarga de enviar el archivo para su descarga
    return send_from_directory(community_library_path, filename, as_attachment=True)


# ------------------ ASSIGNMENTS ------------------

assignments = []
classes = ["Class 1", "Class 2", "Class 3"]

@app.route('/assignments')
def assignments_page():
    user_type = session.get('user_type', 'student')
    if user_type != 'student':
        return redirect(url_for('home'))

    # Filtrar tareas por clase si tienes esa lógica
    class_name = request.args.get('class', 'Class 1')
    class_assignments = [a for a in assignments if a.get('class') == class_name]

    return render_template('assignments.html',
                           assignments=class_assignments,
                           classes=classes,
                           current_class=class_name,
                           user_type=user_type)


@app.route('/assignments_teacher')
def assignments_teacher():
    user_type = session.get('user_type')
    if user_type != 'teacher':
        return redirect(url_for('home'))

    return redirect(url_for('assignments_by_class', class_name='Class 1'))


@app.route('/assignments/<class_name>')
def assignments_by_class(class_name):
    if class_name not in classes:
        flash("Invalid class")
        return redirect(url_for('assignments_teacher'))

    user_type = session.get('user_type', 'student')
    if user_type != 'teacher':
        return redirect(url_for('home'))

    # Filtrar asignaciones por clase
    class_assignments = [a for a in assignments if a['class'] == class_name]

    assignment_data = []
    for assignment in class_assignments:
        folder = assignment['title'].replace(" ", "_")
        folder_path = os.path.join("uploads", folder)
        submissions = {}
        if os.path.exists(folder_path):
            for student in os.listdir(folder_path):
                student_path = os.path.join(folder_path, student)
                if os.path.isdir(student_path):
                    files = os.listdir(student_path)
                    submissions[student] = files
        assignment_data.append({
            'title': assignment['title'],
            'description': assignment['description'],
            'submissions': submissions
        })

    return render_template('assignments5.html',
                           assignments=assignment_data,
                           classes=classes,
                           current_class=class_name,
                           user_type='teacher')


@app.route('/post_assignment', methods=['POST'])
def post_assignment():
    user_type = session.get('user_type')
    if user_type != 'teacher':
        return redirect(url_for('home'))

    title = request.form.get('title')
    description = request.form.get('description')
    class_name = request.form.get('class_name')

    if title and description and class_name:
        assignments.append({
            'title': title,
            'description': description,
            'class': class_name
        })

    return redirect(url_for('assignments_by_class', class_name=class_name))

@app.route('/submit_assignment', methods=['POST'])
def submit_assignment():
    if session.get('user_type') != 'student':
        return redirect(url_for('home'))
    file = request.files.get('submission')
    title = request.form.get('assignment_title')
    student = session.get('username', 'unknown')
    if title and file:
        folder = os.path.join("uploads", title.replace(" ", "_"), student)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, file.filename)
        file.save(path)
        flash("Assignment submitted.")
    return redirect(url_for('assignments_page'))

@app.route('/download/<assignment>/<student>/<filename>')
def download_file(assignment, student, filename):
    folder = os.path.join("uploads", assignment, student)
    return send_from_directory(folder, filename, as_attachment=True)

# ------------------ HOME ROUTES ------------------

@app.route('/home_student')
def home_student():
    if session.get('user_type') != 'student':
        return redirect(url_for('home'))

    username = session.get('username')
    student_data = users.get('student', {})
    student_class = student_data.get('class', 'Class 1')  # valor por defecto
    class_messages = class_forums.get(student_class, [])

    return render_template(
        'home.html',
        user_type='student',
        username=username,
        messages=class_messages,
        student_class=student_class
    )


@app.route('/home_teacher')
def home_teacher():
    return redirect(url_for('class_forum', class_name='Class 1'))

@app.route('/home_normal')
def home_normal():
    if session.get('user_type') != 'normal':
        return redirect(url_for('home'))
    return render_template('community_home.html', user_type='normal')

@app.route('/community_home')
def community_home():
    return render_template('community_home.html', user_type='normal')

@app.route('/member_home')
def member_home():
    return render_template('memberHome.html', user_type='normal')


@app.route('/WWFCommunityPage')
def wwf_community_page():
    user_type = session.get('user_type', 'normal')
    user = users.get(user_type, {})
    forum_messages = community_forums.get('wwf', [])  # 👈 se saca de la estructura correcta
    return render_template('wwf_community.html', user=user, messages=forum_messages)



community_forums = {
    'wwf': []
}

@app.route('/post_to_forum', methods=['POST'])
def post_to_forum():
    user_type = session.get('user_type')
    username = session.get('username', 'anonymous')
    text = request.form.get('postText')
    image = request.files.get('fileInput')
    community = request.form.get('redirect_community', 'wwf')

    post = {
        'username': username,
        'text': text,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'image_filename': None
    }

    if image and image.filename:
        filename = secure_filename(image.filename)
        folder = os.path.join("static", "forum_images")
        os.makedirs(folder, exist_ok=True)
        image_path = os.path.join(folder, filename)
        image.save(image_path)
        post['image_filename'] = f"forum_images/{filename}"

    if user_type == 'student':
        student_class = users.get('student', {}).get('class', 'Class 1')
        class_forums[student_class].append(post)
        return redirect(url_for("home_student"))

    elif user_type == 'teacher':
        return redirect(url_for("home_teacher"))

    else:
        if community not in community_forums:
            community_forums[community] = []
        community_forums[community].append(post)
        return redirect(url_for(f"{community}_community_page"))


if __name__ == '__main__':
    app.run(debug=True)
