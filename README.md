
# KomodoHub Flask Web Application

## 📁 Application Structure Overview

```
final_app
├── app
│   ├── __init__.py      # Initializes the Flask app, configures extensions
│   ├── models.py        # Defines database tables and relationships
│   ├── routes.py        # Defines application endpoints and their logic
│   ├── forms
│   │   └── forms.py     # Defines forms using Flask-WTF
│   ├── static
│   │   ├── css          # Stylesheets
│   │   └── images       # Images and icons
│   └── templates        # HTML templates using Jinja2
│       ├── base.html
│       ├── community_forum.html
│       ├── login.html
│       ├── register.html
│       └── (other templates...)
├── migrations           # Database migrations
├── config.py            # Configurations like database URI and secret key
├── seed.py              # Database seeding script
└── run.py               # Application entry point
```

---

## 🧠 File-by-file Descriptions

### `__init__.py`
- Initializes the Flask app and extensions like SQLAlchemy and Flask-Migrate.
- Loads configuration from `config.py`.

### `models.py`
- Defines SQLAlchemy ORM models:
  - Users: `Teacher`, `Student`, `CommunityUser`
  - Community: `Community`, `CommunityMembership`, `CommunityPost`, `CommunityLibraryFile`
  - Coursework: `Class`, `Assignment`, `Submission`, `Post`, `Attachment`
- Includes relationships and foreign key constraints.

### `routes.py`
- Defines Flask routes and logic for handling all user interactions:
  - Authentication (`/login`, `/logout`)
  - Registration (`/register/*`)
  - Community management, class management, forums, assignments, file uploads
  - Session-based access control for different user types

### `forms/forms.py`
- WTForms definitions for:
  - Login, registration, assignment and class creation
  - Post creation and file uploads
  - Form validation and CSRF protection

### `templates/`
- Contains all Jinja2 HTML templates.
- Uses `base.html` for layout inheritance.
- Templates are rendered conditionally based on user roles.

### `static/`
- Stylesheets (CSS) and static image assets.

### `migrations/`
- Alembic-powered folder for tracking schema changes.

### `config.py`
- Holds global settings:
  - `SQLALCHEMY_DATABASE_URI` (SQLite/MariaDB)
  - `SECRET_KEY`
  - Debug and track modifications

### `run.py`
- Entry point to run the Flask application using CLI or directly.

### `seed.py`
- Script to populate the database with mock users and data for development/testing.

---

## 🔐 Application Logic

### Authentication:
- Users (Teachers, Students, Community Users) register with different forms.
- Session-based login/logout.
- Optional OTP verification (`/otp-verify`).

### Role-Based Access Control:
- **Teachers**: manage classes, students, forums, assignments.
- **Students**: access assignments and participate in class forums.
- **Community Users**: join communities, use forums, upload files.

### Forum Logic:
- Teachers and students can post in class-specific forums.
- Community users can post in community forums.
- Users can only delete their own posts.

### File Management:
- Secure file uploads via `secure_filename()`.
- Attachments stored under specific folders in `static/uploads`.

### Forms:
- Flask-WTF used for all forms with CSRF protection and validation.

### Database Interaction:
- SQLAlchemy ORM used for querying, inserting, and deleting records.
- Migrations managed via Alembic.

---

## 🌐 Flask Routes Summary

### Authentication and Accounts
| Endpoint | Method | Path |
|----------|--------|------|
| `register_gateway` | GET | /register |
| `reg_student` | GET/POST | /register/student |
| `reg_teacher` | GET/POST | /register/teacher |
| `reg_public_user` | GET/POST | /register/community |
| `login` | GET/POST | /login |
| `logout` | GET | /logout |
| `otp_verify` | GET/POST | /otp-verify |
| `account_settings` | GET/POST | /account-settings |

### Teacher Functionalities
| Endpoint | Method | Path |
|----------|--------|------|
| `teacher_classes` | GET/POST | /teacher/classes |
| `manage_class` | GET/POST | /teacher/classes/<id> |
| `remove_student` | GET | /teacher/classes/<id>/remove/<sid> |
| `class_forum` | GET/POST | /teacher/classes/<id>/forum |
| `edit_post` | GET/POST | /teacher/classes/<id>/edit_post/<pid> |
| `delete_post` | POST | /teacher/classes/<id>/posts/<pid>/delete |
| `class_assignments` | GET/POST | /teacher/classes/<id>/assignments |
| `edit_assignment` | GET/POST | /teacher/assignment/<id>/edit |
| `delete_assignment` | POST | /teacher/assignment/<id>/delete |
| `view_submissions` | GET | /teacher/assignment/<id>/submissions |
| `teacher_students` | GET | /teacher/students |
| `teacher_programs` | GET | /teacher/programs |

### Student Functionalities
| Endpoint | Method | Path |
|----------|--------|------|
| `student_forum` | GET/POST | /student/my-class/forum |
| `my_assignments` | GET | /student/my-assignments |
| `upload_submission` | POST | /student/assignments/<id>/submit |
| `delete_submission` | POST | /student/submissions/<id>/delete |

### Community Functionalities
| Endpoint | Method | Path |
|----------|--------|------|
| `community_home` | GET | /community |
| `join_community` | GET | /community/join/<id> |
| `leave_community` | GET | /community/leave/<id> |
| `community_forum` | GET/POST | /community/<id>/forum |
| `delete_community_post` | POST | /community/<id>/post/<pid>/delete |
| `community_library` | GET/POST | /community/<id>/library |
| `delete_community_file` | POST | /community/<id>/library/delete/<fid> |

### Library Resources
| Endpoint | Method | Path |
|----------|--------|------|
| `library` | GET/POST | /library |
| `delete_library_file` | POST | /library/delete/<filename> |

### Static
| Endpoint | Method | Path |
|----------|--------|------|
| `static` | GET | /static/<path:filename> |

---

## 📊 Data Flow Summary

```mermaid
flowchart TD
    Client[User in Browser]
    UI[HTML + JS Templates]
    Routes[Flask Routes (routes.py)]
    Forms[WTForms (forms.py)]
    DB[Database (models.py via SQLAlchemy)]
    Templates[HTML Templates (templates/*.html)]

    Client -->|Request| Routes
    Routes -->|Render| Templates
    Routes --> Forms
    Forms -->|Validate| Routes
    Routes --> DB
    DB --> Routes
    Routes -->|Response| Client
```

---

## 🧪 Running the App

```bash
# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Create and seed the database
flask db init
flask db migrate -m "initial migration"
flask db upgrade
python seed.py  # (optinal, used to populate database)

# Run the server
flask run
```

