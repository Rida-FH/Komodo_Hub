from app import create_app, db
from app.models import Teacher, Student, CommunityUser, Community
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Clear tables (optional)
    Teacher.query.delete()
    Student.query.delete()
    CommunityUser.query.delete()
    Community.query.delete()

    # Add users and communities (same as before)
    teachers = [
        Teacher(email='teacher1@coventry.ac.uk', full_name='Alice Johnson',
                password=generate_password_hash('password123'),
                teacher_id='T1001', profile_picture='default_teacher.png'),
        Teacher(email='teacher2@coventry.ac.uk', full_name='Bob Smith',
                password=generate_password_hash('password123'),
                teacher_id='T1002', profile_picture='default_teacher.png'),
    ]

    students = [
        Student(email='student1@coventry.ac.uk', username='student1',
                password=generate_password_hash('password123'),
                student_id='S2001', profile_picture='default_student.png'),
        Student(email='student2@coventry.ac.uk', username='student2',
                password=generate_password_hash('password123'),
                student_id='S2002', profile_picture='default_student.png'),
    ]

    community_users = [
        CommunityUser(email='commuser1@example.com', username='comm1',
                      password=generate_password_hash('password123'),
                      profile_picture='default_community.png'),
        CommunityUser(email='commuser2@example.com', username='comm2',
                      password=generate_password_hash('password123'),
                      profile_picture='default_community.png'),
    ]

    communities = [
        Community(name='Tiger Talk', description='A community for discussing tiger sightings and facts.'),
        Community(name='Art Club', description='Share and appreciate all forms of animal drawings.'),
        Community(name='Komodo Fans', description='For those whose favourite animal is the great komodo dragon.'),
    ]

    db.session.add_all(teachers + students + community_users + communities)
    db.session.commit()
    print("✅ Database seeded.")
