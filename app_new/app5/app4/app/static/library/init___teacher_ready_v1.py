from flask import Flask, render_template, request, redirect, url_for, session, flash  # Añade flash aquí
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static', 'library')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'  # Required for session management

# Simulated user database
users = {
    'student': {'username': 'student_user', 'email': 'student@email.com', 'join_date': '2023-10-01', 'user_type': 'student'},
    'normal': {'username': 'regular_user', 'email': 'regular@email.com', 'join_date': '2023-10-01', 'user_type': 'normal'}
}

# List to store forum messages
messages = []

# Example communities data
communities = [
    {"name": "Programming Community", "description": "Discuss programming and software development.", "members": 120},
    {"name": "Graphic Design Community", "description": "Share and learn about graphic design.", "members": 85},
    {"name": "Data Science Community", "description": "Explore data science and machine learning.", "members": 200}
]

@app.route('/')
def index():
    return redirect(url_for('home'))  # Redirect to the home page

@app.route('/home')
def home():
    # Get the user type from the session (default to 'student' if not set)
    user_type = session.get('user_type', 'student')
    user = users[user_type]  # Get user data based on type

    # Initialize joined_communities in session if it doesn't exist
    if 'joined_communities' not in session:
        session['joined_communities'] = []

    # Render the appropriate home page based on user type
    if user_type == 'student':
        return render_template('home.html', username=user['username'], messages=messages, user_type=user_type)
    else:
        return render_template('home2.html', username=user['username'], communities=communities, user_type=user_type)

@app.route('/account')
def account():
    user_type = session.get('user_type', 'student')
    user = users[user_type]
    return render_template('account.html', username=user['username'], email=user['email'], user_type=user_type)


@app.route('/change_password', methods=['POST'])
def change_password():
    # Aquí va la lógica para cambiar la contraseña
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    # Verifica que la nueva contraseña y la confirmación coincidan
    if new_password != confirm_password:
        flash('Las contraseñas no coinciden')
        return redirect(url_for('account'))

    # Aquí puedes agregar la lógica para actualizar la contraseña en la base de datos
    # Por ejemplo:
    # user = get_current_user()
    # user.set_password(new_password)
    # db.session.commit()

    flash('Contraseña cambiada exitosamente')
    return redirect(url_for('account'))

@app.route('/join_community/<community_name>')
def join_community(community_name):
    # Add the community to the user's joined_communities list
    if 'joined_communities' not in session:
        session['joined_communities'] = []
    
    if community_name not in session['joined_communities']:
        session['joined_communities'].append(community_name)
    
    return redirect(url_for('home'))

@app.route('/leave_community/<community_name>')
def leave_community(community_name):
    # Remove the community from the user's joined_communities list
    if 'joined_communities' in session and community_name in session['joined_communities']:
        session['joined_communities'].remove(community_name)
    
    return redirect(url_for('home'))

@app.route('/update_profile_picture', methods=['POST'])
def update_profile_picture():
    if 'profile_picture' not in request.files:
        flash('No file part')
        return redirect(url_for('account'))
    
    file = request.files['profile_picture']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('account'))
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        flash('Profile picture updated successfully')
    
    return redirect(url_for('account'))




@app.route('/library')
def library():
    # Only students can access the library
    user_type = session.get('user_type', 'student')
    if user_type != 'student':
        return redirect(url_for('home'))  # Redirect non-student users to home

    # Path to the library folder
    folder_path = os.path.join(app.static_folder, 'library')
    
    # Get the list of files and folders
    try:
        files = os.listdir(folder_path)
    except FileNotFoundError:
        files = []

    return render_template('library.html', files=files, user_type=user_type)

@app.route('/assignments')
def assignments():
    # Only students can access assignments
    user_type = session.get('user_type', 'student')
    if user_type != 'student':
        return redirect(url_for('home'))  # Redirect non-student users to home

    # Example assignment data
    assignments = [
        {"title": "ASSIGNMENT 1", "description": "SCANNT"},
        {"title": "ASSIGNMENT 2", "description": "ISUANT"}
    ]
    return render_template('assignments.html', assignments=assignments, user_type=user_type)

@app.route('/update_username', methods=['POST'])
def update_username():
    user_type = session.get('user_type', 'student')
    user = users[user_type]
    new_username = request.form.get('new_username')
    if new_username:
        user['username'] = new_username
        session['username'] = new_username
    return redirect(url_for('account'))

@app.route('/post_message', methods=['POST'])
def post_message():
    user_type = session.get('user_type', 'student')
    user = users[user_type]
    message = request.form.get('message')
    if message:
        messages.append({'username': user['username'], 'message': message, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    return redirect(url_for('home'))


@app.route('/login/<user_type>')
def login(user_type):
    if user_type in users:
        session['user_type'] = user_type
        session['username'] = users[user_type]['username']
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)






@app.route('/library_teacher')
def library_teacher():
    user_type = session.get('user_type', 'student')
    if user_type != 'teacher':
        return redirect(url_for('home'))

    folder_path = os.path.join(app.static_folder, 'library')

    try:
        files = os.listdir(folder_path)
    except FileNotFoundError:
        files = []

    return render_template('library_teacher.html', files=files, user_type=user_type)

@app.route('/upload_file', methods=['POST'])
def upload_file():
    user_type = session.get('user_type', 'student')
    if user_type != 'teacher':
        flash('Only teachers can upload files.')
        return redirect(url_for('home'))

    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('library_teacher'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('library_teacher'))

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        flash('File uploaded successfully!')

    return redirect(url_for('library_teacher'))