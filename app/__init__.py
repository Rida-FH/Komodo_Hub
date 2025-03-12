# routes
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/register')
def register():
    return render_template('register.html')  

@app.route('/login')
def login():
    return render_template('login.html')  

@app.route('/reg_public_userister')
def reg_public_user():
    return render_template('reg_public_user.html')

@app.route('/student_register')
def student_reg():
    return render_template('reg_student.html')  

@app.route('/student_authentication')
def student_auth():
    return render_template('student_auth.html') 

@app.route('/teacher_register')
def teacher_reg():
    return render_template('reg_teacher.html') 