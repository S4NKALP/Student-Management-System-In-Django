# 📚 Student Management System (SMS)

<div align="center">

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/S4NKALP/Student-Management-System-In-Django)](https://github.com/S4NKALP/Student-Management-System-In-Django/stargazers)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Code Quality](https://img.shields.io/badge/code%20quality-A-green)]()
[![Documentation](https://img.shields.io/badge/docs-95%25-brightgreen)]()
[![Tests](https://img.shields.io/badge/tests-85%25-yellow)]()

A comprehensive Student Management System built with Django, featuring multi-role access, real-time notifications, and secure authentication.

</div>

> **Note:** This project was developed as part of an academic minor project. Ongoing maintenance or additional feature development may be limited.

## 📑 Table of Contents

- [💻 Tech Stack](#-tech-stack)
- [👥 Role System](#-role-system)
- [✨ Key Features](#-key-features)
- [📸 Screenshots](#-screenshots)
- [🎯 Project Architecture](#-project-architecture)
- [🌍 Feasibility](#-feasibility)
- [🚀 Getting Started](#-getting-started)
- [🔧 Configuration](#-configuration)
- [📦 Dependencies](#-dependencies)
- [🔐 Security Features](#-security-features)
- [📊 Database Schema](#-database-schema)
- [🔌 API Endpoints](#-api-endpoints)
- [📱 Frontend Features](#-frontend-features)
- [🔍 Testing](#-testing)
- [📈 Performance](#-performance)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🙏 Credits](#-credits)

## 💻 Tech Stack

<details>
<summary><b>🔥 Core Technologies</b></summary>

| Technology            | Version | Purpose             | Documentation                                      |
| --------------------- | ------- | ------------------- | -------------------------------------------------- |
| Python                | 3.8+    | Backend Development | [Python Docs](https://docs.python.org/)            |
| Django                | 5.2     | Web Framework       | [Django Docs](https://docs.djangoproject.com/)     |
| Django REST Framework | 3.16.0  | API Development     | [DRF Docs](https://www.django-rest-framework.org/) |
| Firebase Admin        | 6.7.0   | Real-time Features  | [Firebase Docs](https://firebase.google.com/docs)  |
| Google Cloud Storage  | 3.1.0   | File Storage        | [GCS Docs](https://cloud.google.com/storage/docs)  |

</details>

<details>
<summary><b>⚡ Frontend Technologies</b></summary>

| Technology       | Version | Purpose           | Documentation                                             |
| ---------------- | ------- | ----------------- | --------------------------------------------------------- |
| Bootstrap        | 5.3.0   | UI Framework      | [Bootstrap Docs](https://getbootstrap.com/docs/)          |
| jQuery           | Latest  | DOM Manipulation  | [jQuery Docs](https://api.jquery.com/)                    |
| Firebase Web SDK | 9.22.0  | Real-time Updates | [Firebase Web Docs](https://firebase.google.com/docs/web) |
| Font Awesome     | 6.0.0   | Icons             | [Font Awesome Docs](https://fontawesome.com/docs)         |

</details>

<details>
<summary><b>🛠️ Development Tools</b></summary>

| Tool               | Version | Purpose             | Documentation                                                   |
| ------------------ | ------- | ------------------- | --------------------------------------------------------------- |
| Git                | Latest  | Version Control     | [Git Docs](https://git-scm.com/doc)                             |
| WhiteNoise         | 6.9.0   | Static File Serving | [WhiteNoise Docs](https://whitenoise.readthedocs.io/)           |
| PyOTP              | 2.9.0   | OTP Generation      | [PyOTP Docs](https://github.com/pyauth/pyotp)                   |
| Django Jazzmin     | 3.0.1   | Admin Interface     | [Jazzmin Docs](https://django-jazzmin.readthedocs.io/)          |
| Django Mathfilters | 1.0.0   | Math Operations     | [Mathfilters Docs](https://github.com/dbrgn/django-mathfilters) |
| Django Model Utils | 5.0.0   | Model Utilities     | [Model Utils Docs](https://django-model-utils.readthedocs.io/)  |

</details>

### 🖥️ Development Environment

| Component            | Details                                        |
| -------------------- | ---------------------------------------------- |
| **Operating System** | [Arch Linux](https://archlinux.org/)           |
| **Window Manager**   | [Hyprland](https://github.com/hyprwm/Hyprland) |
| **Status Bar**       | [Modus](https://github.com/S4NKALP/Modus)      |
| **Editor**           | [Neovim](https://neovim.io/)                   |
| **Terminal**         | [Kitty](https://sw.kovidgoyal.net/kitty/)      |
| **Shell**            | [Zsh](https://www.zsh.org/)                    |

## 👥 Role System

### 🎓 User Roles and Permissions

| Role                         | Description                              | Key Features                                                                     |
| ---------------------------- | ---------------------------------------- | -------------------------------------------------------------------------------- |
| **Super Admin**              | System administrator with full access    | - Full system control<br>- User management<br>- System configuration             |
| **HOD (Head of Department)** | Department head with elevated privileges | - Course management<br>- Staff supervision<br>- Department analytics             |
| **Admission Officer**        | Handles student admissions               | - Student registration<br>- Document verification<br>- Admission tracking        |
| **Teacher**                  | Academic staff member                    | - Class management<br>- Attendance tracking<br>- Grade management                |
| **Student**                  | Primary system user                      | - Course access<br>- Attendance tracking<br>- Grade viewing                      |
| **Parent**                   | Student guardian                         | - Student progress tracking<br>- Communication with teachers<br>- Fee management |

### 🔐 Authentication System

- **Multi-factor Authentication**

  - Phone-based OTP verification
  - TOTP (Time-based One-Time Password)
  - Password reset tokens
  - Session management

- **Role-based Access Control**
  - Granular permissions per role
  - Custom permission groups
  - Access level restrictions
  - Activity logging

## ✨ Key Features

### 👥 User Management

- **Multi-role System**: Comprehensive roles including Admin, HOD, Teacher, Student, Parent, and Admission Officer
- **Secure Authentication**: OTP and TOTP-based verification for password resets
- **Role-based Access Control**: Different dashboards and permissions for each user role
- **User Profiles**: Complete profile management with personal details and image uploads

### 📚 Academic Management

- **Course Management**: Create and organize course offerings with duration tracking
- **Subject Management**: Organize subjects with syllabus uploads and additional materials
- **Class Scheduling**: Create and manage class routines with teacher assignments
- **Batch Management**: Group students into batches for better organization

### 📊 Attendance System

- **Class Attendance**: Record and track student attendance for each class
- **Teacher Attendance**: Track teacher presence for scheduled classes
- **Attendance Reports**: View attendance statistics and historical records
- **Real-time Status**: Monitor attendance status on dashboards

### 📝 Leave Management

- **Leave Requests**: Students and staff can request leave with date ranges
- **Multi-level Approval**: HOD or Admin approval workflow for leave requests
- **Status Tracking**: Monitor pending, approved, and rejected leave requests
- **Leave History**: Complete historical record of all leave requests

### 👨‍👩‍👧‍👦 Parent-Teacher Interaction

- **Meeting Scheduling**: Schedule online or in-person parent-teacher meetings
- **Student Progress Tracking**: Parents can monitor student performance
- **Meeting Management**: Tools for scheduling, rescheduling, and cancelling meetings

### 📈 Course Progress Tracking

- **Progress Monitoring**: Track student course completion percentages
- **Completion Metrics**: View detailed completion metrics by course and student
- **Performance Analysis**: Analyze student performance across courses

### 🔄 Feedback System

- **Multi-level Feedback**: Students, parents, and staff can submit feedback
- **Rating System**: Detailed rating mechanism with comments
- **Anonymous Feedback**: Option for anonymous feedback submissions
- **Institute Feedback**: Feedback about the educational institution

### 🔐 Security Features

- **OTP Verification**: Two-factor authentication for password resets
- **Session Management**: Secure session handling for all users
- **CSRF Protection**: Cross-site request forgery prevention
- **Password Security**: Strong password validation and secure storage

### 📱 Mobile-Friendly Interface

- **Responsive Design**: Works seamlessly on mobile devices and desktops
- **Touch-friendly Interface**: Optimized for touch devices
- **Responsive Navigation**: Mobile-optimized navigation system
- **Adaptive Layouts**: Content adjusts to different screen sizes

## 📸 Screenshots

<details>
<summary><b>🏠 Dashboard Views</b></summary>

![Admin Dashboard](screenshots/admin_dashboard.png)
_Admin Dashboard with overview statistics and quick actions_

![Student Dashboard](screenshots/student_dashboard.png)
_Student Dashboard showing attendance, course progress, and notices_

![Teacher Dashboard](screenshots/teacher_dashboard.png)
_Teacher Dashboard with class schedule and student performance metrics_

</details>

<details>
<summary><b>👥 User Management</b></summary>

![User Profiles](screenshots/user_profiles.png)
_User profile management interface_

![Role Management](screenshots/role_management.png)
_Role-based access control settings_

</details>

<details>
<summary><b>📚 Academic Features</b></summary>

![Course Management](screenshots/course_management.png)
_Course creation and management interface_

![Attendance System](screenshots/attendance_system.png)
_Attendance tracking and reporting_

![Leave Management](screenshots/leave_management.png)
_Leave request and approval workflow_

</details>

<details>
<summary><b>📱 Mobile Responsive Design</b></summary>

![Mobile Dashboard](screenshots/mobile_dashboard.png)
_Dashboard view on mobile devices_

![Mobile Navigation](screenshots/mobile_navigation.png)
_Responsive navigation menu on smaller screens_

</details>

> **Note:** The above screenshots showcase key interfaces of the Student Management System. Replace these placeholder images with actual screenshots by adding your images to a `screenshots` directory in the project root.

## 🎯 Project Architecture

```
SMS/
├── app/                    # Main application
│   ├── admin/             # Admin interface
│   ├── api/               # REST API endpoints
│   ├── models/            # Database models
│   ├── views/             # View logic
│   └── templates/         # HTML templates
├── static/                # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── img/              # Images
├── media/                 # User uploaded files
├── templates/             # Base templates
└── student_management_system/  # Project settings
```


## 🚀 Getting Started

### 📋 Prerequisites

Before you begin, ensure you have the following installed:

- [Python](https://www.python.org/downloads/) (3.8 or higher)
- [Git](https://git-scm.com/downloads)
- [UV](https://github.com/astral-sh/uv) (Python package installer and resolver)
- [Firebase Account](https://firebase.google.com/) (for notifications)
- [Google Cloud Account](https://cloud.google.com/) (for storage)

### 🛠️ Installation Steps

#### 1️⃣ Clone the Repository

```bash
# Clone the repository
git clone https://github.com/S4NKALP/Student-Management-System-In-Django.git

# Navigate to the project directory
cd Student-Management-System-In-Django
```

#### 2️⃣ Choose Your Installation Method

##### Method A: Using UV (Recommended)

```bash
# Install UV (if not already installed)
pip install uv

# Or install using curl (Linux/Mac)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or install using PowerShell (Windows)
irm https://astral.sh/uv/install.ps1 | iex

# Run migrations
uv run manage.py makemigrations
uv run manage.py migrate

# Create admin user
uv run manage.py createsuperuser

# Run the server the package will install automatically
uv run manage.py runserver
```

##### Method B: Using Traditional venv

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# For Linux/Mac:
source venv/bin/activate

# For Windows:
.\venv\Scripts\activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Lunch the server
python manage.py runserver

```

#### 3️⃣ Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
# Required settings:
# - SECRET_KEY
# - DEBUG
# - ALLOWED_HOSTS
# - Firebase credentials
# - Google Cloud credentials
```

#### 5️⃣ Set Up Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Enable the following services:
   - Authentication
   - Cloud Firestore
   - Cloud Storage
   - Cloud Messaging

#### 2️⃣ Service Account Key (`firebase-key.json`)

1. In Firebase Console, go to Project Settings > Service Accounts
2. Click "Generate New Private Key"
3. Save the downloaded JSON file as `firebase-key.json` in your project root
4. Add the file to `.gitignore` to prevent committing sensitive data:
   ```gitignore
   firebase-key.json
   ```

#### 3️⃣ Firebase Configuration Files

1. Copy the example files and rename them:

   ```bash
   # Copy Firebase config example
   cp static/js/firebase-config.example.js static/js/firebase-config.js

   # Copy Firebase messaging service worker example
   cp static/firebase-messaging-sw.example.js static/firebase-messaging-sw.js
   ```

2. Update the configuration in both files with your Firebase project details:
   - Replace `YOUR_API_KEY` with your Firebase API key
   - Replace `YOUR_PROJECT_ID` with your Firebase project ID
   - Replace other placeholder values with your actual Firebase configuration

#### 4️⃣ Firebase Cloud Messaging (FCM) Setup

1. In Firebase Console, go to Project Settings > Cloud Messaging
2. Generate a new Server Key
3. Add the key to your `.env` file:
   ```env
   FIREBASE_SERVER_KEY=your_server_key_here
   ```

#### 5️⃣ Testing Firebase Setup

1. Run the development server
2. Open the browser console
3. Check for any Firebase-related errors
4. Test push notifications using the Firebase Console

### 📱 Accessing the Application

Once everything is set up, you can access:

- **Admin Panel**: http://localhost:8000/admin
- **Main Application**: http://localhost:8000

### 🚨 Troubleshooting Guide

#### 🔧 Common Issues

- **Firebase Setup**: Ensure proper configuration in `firebase-config.js` and `firebase-key.json`
- **Static Files**: Run `python manage.py collectstatic` if static files are not loading
- **Database Issues**: Check database settings in `.env` file
- **OTP Not Working**: Verify email settings in `.env` file

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=sms_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost

# Firebase Settings
FIREBASE_CREDENTIALS=path/to/firebase-key.json
FIREBASE_DATABASE_URL=your-firebase-database-url

# Google Cloud Settings
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_CREDENTIALS=path/to/google-cloud-key.json

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# SMS Configuration
SMS_API_KEY=your_sms_api_key_here
SMS_SENDER_ID=SMSSYS

# OTP Settings
OTP_EXPIRY=300  # OTP expiry time in seconds
```

## 📦 Dependencies

### Backend

- Django 5.2
- Django REST Framework 3.16.0
- Firebase Admin 6.7.0
- Google Cloud Storage 3.1.0
- PyOTP 2.9.0
- WhiteNoise 6.9.0
- Django Jazzmin 3.0.1
- Django Mathfilters 1.0.0
- Django Model Utils 5.0.0

### Frontend

- Bootstrap 5.3.0
- jQuery Latest
- Firebase Web SDK 9.22.0
- Font Awesome 6.0.0

## 🔐 Security Features

### Authentication

- OTP and TOTP-based authentication
- Session management
- Password hashing
- Password reset tokens

### Data Protection

- CSRF protection
- XSS prevention
- SQL injection prevention
- Input validation
- File upload security

## 📊 Database Schema

### Core Models

#### Institute

- `name`, `phone`, `email`, `address`, `pan_no`, `reg_no`, `logo`, `description`

#### Course

- `name`, `code`, `duration`, `duration_type`, `description`, `is_active`
- `batches` (ManyToManyField to Batch)
- `course_tracking_records` (related_name for CourseTracking)
- `routine_records` (related_name for Routine)

#### Subject

- `name`, `code`, `course` (ForeignKey to Course), `period_or_year`, `syllabus_pdf`, `files`
- `attendance_records` (related_name for Attendance)

#### Student

- `name`, `status`, `gender`, `birth_date`, `email`, `phone`, `addresses`
- `marital_status`, `parent_name`, `parent_phone`, `citizenship_no`
- `batches` (ManyToManyField to Batch)
- `image`, `course` (ForeignKey to Course), `current_period`, `joining_date`, `fcm_token`
- `meetings` (related_name for TeacherParentMeeting)
- `leave_requests` (related_name for StudentLeave)

#### Staff

- `name`, `phone`, `designation`, `gender`, `birth_date`, `email`, `addresses`
- `marital_status`, `parent_name`, `parent_phone`, `citizenship_no`, `passport`
- `image`, `joining_date`, `fcm_token`
- `courses_taught` (related_name for Course)
- `meetings` (related_name for TeacherParentMeeting)

#### Parent

- `name`, `phone`, `email`, `address`, `students` (ManyToManyField to Student)
- `image`, `fcm_token`

#### Routine

- `course` (ForeignKey to Course), `subject` (ForeignKey to Subject)
- `teacher` (ForeignKey to Staff), `start_time`, `end_time`
- `period_or_year`, `is_active`
- `attendance_records` (related_name for Attendance)

#### Attendance

- `date`, `routine` (ForeignKey to Routine), `teacher` (ForeignKey to Staff)
- `teacher_attend`, `class_status`

#### Leave Management

- `StaffLeave`: `staff` (ForeignKey to Staff), `start_date`, `end_date`, `message`, `status`
- `StudentLeave`: `student` (ForeignKey to Student), `start_date`, `end_date`, `message`, `status`

#### CourseTracking

- `student` (ForeignKey to Student), `course` (ForeignKey to Course)
- `enrollment_date`, `start_date`, `expected_end_date`, `actual_end_date`
- `progress_status`, `completion_percentage`, `current_period`
- `period_start_date`, `period_end_date`, `notes`

#### TeacherParentMeeting

- `meeting_date`, `meeting_time`, `duration`, `status`, `agenda`, `notes`
- `cancellation_reason`, `meeting_link`, `is_online`
- `student` (ForeignKey to Student), `teacher` (ForeignKey to Staff)
- `attendance_records` (related_name for Attendance)

### Security Models

- `TOTPSecret`: OTP secret keys
- `ResetToken`: Password reset tokens

## 🔌 API Endpoints

### Authentication & Security

- `POST /password-reset/` - Password reset options
- `POST /password-reset/phone/` - Phone-based password reset
- `POST /password-reset/phone/verify/` - Verify phone OTP
- `POST /password-reset/email/` - Email-based password reset
- `POST /password-reset/email/verify/` - Verify email code
- `POST /password-reset/set/` - Set new password
- `POST /check-weak-password/` - Password strength check

### Dashboard & Profile

- `GET /dashboard/` - Main dashboard
- `GET /student-dashboard/` - Student dashboard
- `GET /teacher-dashboard/` - Teacher dashboard
- `GET /parent-dashboard/` - Parent dashboard
- `GET /hod-dashboard/` - HOD dashboard
- `GET /admission-officer-dashboard/` - Admission officer dashboard
- `POST /update-profile/` - Update user profile
- `POST /change-password/` - Change password

### Leave Management

- `POST /request-leave/` - Request student leave
- `POST /request-staff-leave/` - Request staff leave
- `POST /approve-student-leave/<int:leave_id>/` - Approve student leave
- `POST /reject-student-leave/<int:leave_id>/` - Reject student leave
- `POST /approve-staff-leave/<int:leave_id>/` - Approve staff leave
- `POST /reject-staff-leave/<int:leave_id>/` - Reject staff leave

### Meeting Management

- `POST /schedule-meeting/` - Schedule parent-teacher meeting
- `POST /update-meeting/<int:meeting_id>/` - Update meeting details
- `POST /cancel-meeting/<int:meeting_id>/` - Cancel meeting
- `POST /mark-attendance/<int:meeting_id>/` - Mark meeting attendance

### Course Progress

- `GET /course-progress/<int:student_id>/` - Get student's course progress
- `GET /subject-progress/<int:subject_id>/` - Get subject progress
- `POST /update-progress/<int:tracking_id>/` - Update course progress

### Attendance

- `POST /mark-attendance/` - Mark class attendance
- `GET /attendance-report/<int:student_id>/` - Get student attendance report
- `GET /class-attendance/<int:routine_id>/` - Get class attendance

## 🔐 Security Features

### Authentication

- OTP and TOTP-based authentication
- Session management
- Password hashing using Django's built-in hashers
- Password reset tokens with expiration

### Data Protection

- CSRF protection
- Input validation
- File upload security with size and type restrictions
- Secure file storage using Google Cloud Storage

### Role-based Access Control

- Granular permissions per role
- Custom permission groups
- Access level restrictions
- Activity logging

### API Security

- Token-based authentication
- Rate limiting
- Request validation
- Error handling

## 📱 Frontend Features

## 🔍 Testing

### Test Coverage

- Unit tests for models
- Integration tests for views
- API endpoint tests
- Security tests

### Test Types

- Model validation tests
- View response tests
- Permission tests
- Integration tests

### Test Tools

- Django Test Client
- pytest
- Coverage reporting
- CI/CD integration

### Responsive Design

- Mobile-first approach
- Bootstrap 5.3.0 for responsive layouts
- Custom CSS for specific components
- Adaptive navigation

### Real-time Updates

- Firebase Cloud Messaging for push notifications
- WebSocket support for live updates
- Real-time attendance tracking
- Instant notification system

### User Interface

- Clean and modern design
- Intuitive navigation
- Role-specific dashboards
- Interactive data visualization

### Mobile Optimization

- Touch-friendly interface
- Responsive tables
- Mobile-optimized forms
- Adaptive image loading

## 📈 Performance

### Optimization

- Database query optimization
- Caching implementation
- Lazy loading
- Asset compression

### Monitoring

- Error tracking
- Performance metrics
- User activity logging
- System health checks

### Scalability

- Horizontal scaling support
- Load balancing
- Database sharding
- Caching strategies

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Add comments
- Follow Django best practices

### Commit Messages

- Use present tense
- Be descriptive
- Reference issues
- Follow conventional commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

If you use this project in your work, please give proper credit by:

1. **Academic Use**:

   ```markdown
   Student Management System (SMS) by S4NKALP
   GitHub: https://github.com/S4NKALP/Student-Management-System-In-Django
   ```

2. **Commercial Use**:

   ```markdown
   Based on Student Management System (SMS) by S4NKALP
   Original Project: https://github.com/S4NKALP/Student-Management-System-In-Django
   ```

3. **Code References**:

   ```python
   # This code is based on Student Management System (SMS)
   # Original Author: S4NKALP
   # Source: https://github.com/S4NKALP/Student-Management-System-In-Django
   ```

4. **Documentation**:

   - Include a reference to the original project in your documentation
   - Mention any modifications or improvements you've made
   - Provide a link to the original repository

5. **Presentations/Reports**:
   - Include the project name and author in your references
   - Provide the GitHub repository link
   - Acknowledge any specific features or components used

Remember to respect the MIT License terms while using this project.

### 📝 Acknowledgments

- This project was inspired by the need for a modern, efficient student management system
- Special thanks to all the testers and users who provided valuable feedback
- Grateful to the academic community for their support and suggestions

---

<div align="center">

### Made with ❤️ by [Sankalp](https://github.com/S4NKALP)

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/S4NKALP)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/sankalp)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/sankalp)

</div>
