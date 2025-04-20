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

## 📑 Table of Contents

- [💻 Tech Stack](#-tech-stack)
- [👥 Role System](#-role-system)
- [✨ Key Features](#-key-features)
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
- [🔄 Recent Improvements](#-recent-improvements)

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

- **Multi-role System**: Comprehensive role hierarchy
- **Secure Authentication**: OTP and TOTP-based verification
- **Role-based Access Control**: Detailed permission system
- **User Profiles**: Complete user information management

### 📚 Academic Management

- **Course Management**: Create and manage courses
- **Subject Management**: Organize subjects with materials
- **Class Scheduling**: Advanced timetable system
- **Grade Management**: Comprehensive grading system
- **Exam Management**: Complete exam workflow

### 📊 Attendance System

- **Real-time Tracking**: Live attendance monitoring
- **Automated Reports**: Detailed attendance analytics
- **Notification System**: Real-time alerts
- **Bulk Operations**: Efficient batch processing

### 📝 Leave Management

- **Multi-level Approval**: Role-based approval workflow
- **Leave History**: Complete leave tracking
- **Automated Notifications**: Status updates
- **Documentation**: Leave record management

### 👨‍👩‍👧‍👦 Parent-Teacher Interaction

- **Meeting Scheduling**: Online/offline meeting management
- **Progress Tracking**: Student performance monitoring
- **Communication**: Direct messaging system
- **Feedback System**: Comprehensive feedback mechanism

### 📈 Course Progress Tracking

- **Progress Monitoring**: Real-time course progress
- **Completion Tracking**: Detailed completion metrics
- **Performance Analytics**: Student performance analysis
- **Automated Updates**: Progress notifications

### 🔄 Feedback System

- **Multi-level Feedback**: Student, parent, and staff feedback
- **Rating System**: Detailed rating mechanism
- **Anonymous Feedback**: Option for anonymous submissions
- **Feedback Analytics**: Comprehensive feedback analysis

### 🔐 Security Features

- **OTP Verification**: Two-factor authentication
- **Session Management**: Secure session handling
- **CSRF Protection**: Cross-site request forgery prevention
- **XSS Protection**: Cross-site scripting prevention
- **SQL Injection Prevention**: Secure database queries

### 📱 Mobile Features

- **Responsive Design**: Mobile-first approach
- **Push Notifications**: Real-time updates
- **Mobile Optimization**: Touch-friendly interface

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

## 🔄 Recent Improvements

### 🧹 Code Reorganization

- **Reduced Redundancy**: Consolidated duplicate code in view functions
- **Improved Structure**: Created common view utilities and helper functions
- **Better Code Reuse**: Implemented common handlers for common operations
- **Standardized Response Format**: Created consistent API response formats

### ⚡ Performance Optimizations

- **Dependency Management**: Updated and optimized package requirements
- **Firebase Integration**: Enhanced Firebase functionality and error handling
- **View Efficiency**: Reduced redundant database queries
- **API Improvements**: Standardized API response formats for better client handling

### 🔧 Technical Enhancements

- **Role-based Access**: Improved role verification with utility functions
- **Error Handling**: Better error detection and user feedback
- **File Upload Handling**: Centralized file upload handling with validation
- **Password Security**: Enhanced password strength validation

### 🧹 Code Cleanup

- **Removed Print Statements**: Eliminated unnecessary print debug statements
- **Standardized Views**: Consistent view behavior across the application
- **Simplified Middleware**: Streamlined HTTP error handling
- **Better Exception Handling**: More graceful error handling throughout the app

These improvements make the codebase more maintainable, easier to extend, and more efficient in its operation, while maintaining all the original functionality.

## 🚀 Getting Started

### 📋 Prerequisites

Before you begin, ensure you have the following installed:

- [Python](https://www.python.org/downloads/) (3.8 or higher)
- [Git](https://git-scm.com/downloads)
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

#### 2️⃣ Set Up Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# For Linux/Mac:
source venv/bin/activate

# For Windows:
.\venv\Scripts\activate
```

#### 3️⃣ Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

#### 4️⃣ Configure Environment Variables

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

#### Subject

- `name`, `code`, `course`, `period_or_year`, `syllabus_pdf`, `files`

#### Student

- `name`, `status`, `gender`, `birth_date`, `email`, `phone`, `addresses`
- `marital_status`, `parent_name`, `parent_phone`, `citizenship_no`
- `batches`, `image`, `course`, `current_period`, `joining_date`, `fcm_token`

#### Staff

- `name`, `phone`, `designation`, `gender`, `birth_date`, `email`, `addresses`
- `marital_status`, `parent_name`, `parent_phone`, `citizenship_no`, `passport`
- `image`, `joining_date`, `fcm_token`, `course`

#### Parent

- `name`, `phone`, `email`, `address`, `students`, `image`, `fcm_token`

#### Routine

- `course`, `subject`, `teacher`, `start_time`, `end_time`, `period_or_year`, `is_active`

#### Attendance

- `date`, `routine`, `teacher`, `teacher_attend`, `class_status`

#### Leave Management

- `StaffLeave`: `staff`, `start_date`, `end_date`, `message`, `status`
- `StudentLeave`: `student`, `start_date`, `end_date`, `message`, `status`

#### Feedback System

- `StudentFeedback`: Student feedback for teachers
- `ParentFeedback`: Parent feedback for teachers
- `InstituteFeedback`: Student feedback for institute
- `StaffInstituteFeedback`: Staff feedback for institute
- `ParentInstituteFeedback`: Parent feedback for institute

#### Course Tracking

- `student`, `course`, `enrollment_date`, `start_date`, `expected_end_date`
- `actual_end_date`, `progress_status`, `completion_percentage`, `current_period`
- `period_start_date`, `period_end_date`, `notes`

#### Teacher-Parent Meeting

- `meeting_date`, `meeting_time`, `duration`, `status`, `agenda`, `notes`
- `cancellation_reason`, `meeting_link`, `is_online`

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

### Feedback System

- `POST /submit-feedback/` - Submit general feedback
- `POST /submit-institute-feedback/` - Submit institute feedback
- `POST /submit-staff-institute-feedback/` - Submit staff institute feedback
- `POST /submit-parent-feedback/` - Submit parent feedback
- `POST /submit-parent-institute-feedback/` - Submit parent institute feedback

### Subject & Course Management

- `GET /subject/<int:subject_id>/files/` - Get subject files
- `GET /subject/<int:subject_id>/syllabus/` - View subject syllabus
- `GET /get-subjects/` - Get all subjects
- `GET /get-teachers/` - Get all teachers
- `GET /get-course-duration/` - Get course duration
- `GET /get-subject-schedule/` - Get subject schedule
- `POST /manage-subject-files/` - Manage subject files
- `POST /delete-subject-file/` - Delete subject file
- `GET /get-teacher-subjects/` - Get teacher's subjects

### Attendance Management

- `POST /save-attendance/` - Save attendance
- `GET /get-attendance-form/` - Get attendance form
- `GET /get-students/` - Get student list

### Notice Management

- `POST /add-notice/` - Add new notice
- `POST /delete-notice/<int:notice_id>/` - Delete notice

### Parent-Teacher Meeting

- `POST /schedule-meeting/` - Schedule a meeting
- `POST /update-meeting/<int:meeting_id>/` - Update meeting details
- `POST /cancel-meeting/<int:meeting_id>/` - Cancel a meeting
- `GET /get-meetings/` - Get all meetings
- `GET /get-upcoming-meetings/` - Get upcoming meetings

### Course Progress

- `GET /get-course-progress/<int:student_id>/` - Get student's course progress
- `POST /update-course-progress/` - Update course progress
- `GET /get-progress-analytics/` - Get progress analytics

### Firebase Integration

- `POST /saveFCMToken/` - Save Firebase Cloud Messaging token

### 🔐 Authentication System

#### OTP Verification

- Phone-based OTP verification
- OTP expiry management
- OTP resend functionality
- Secure OTP storage

## 📱 Frontend Features

### User Interface

- Responsive design
- Dark/Light mode
- Custom themes
- Accessibility support
- Mobile-first approach

### Interactive Features

- Real-time updates
- File uploads
- Data visualization
- Interactive forms
- Dynamic content loading

### Mobile Optimization

- Touch-friendly interface
- Push notifications
- Mobile-specific layouts
- Gesture support

## 🔍 Testing

### Current Test Coverage

- Unit Tests: Basic test structure in place
- API Tests: Endpoint testing framework available
- Integration Tests: Setup for comprehensive testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test app

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Areas

1. Authentication & Authorization

   - OTP verification
   - Password reset
   - Role-based access

2. Data Management

   - CRUD operations
   - Data validation
   - File handling

3. Business Logic

   - Attendance calculation
   - Leave approval workflow
   - Course progress tracking

4. Integration
   - Firebase messaging
   - File storage
   - Email/SMS notifications

## 📈 Performance

### Optimization Techniques

- Database indexing
- Query optimization
- Caching
- Lazy loading
- Code minification
- Asset compression
- CDN integration

### Monitoring

- Performance metrics
- Error tracking
- User analytics
- Resource usage
- API response times

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

If you use this project in your work, please give credit where credit is due:

```markdown
Student Management System
Created by Sankalp
GitHub: https://github.com/S4NKALP
```

### 📝 Citation

If you're using this project in an academic context, you can cite it as:

```bibtex
@software{StudentManagementSystem2025,
  author = {Sankalp},
  title = {Student Management System},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/S4NKALP/Student-Management-System-In-Django}
}
```

### 🤝 Acknowledgments

- Thanks to all contributors who have helped improve this project
- Special thanks to the open-source community for their valuable resources
- Appreciation to all users who have provided feedback and suggestions

---

<div align="center">

### Made with ❤️ by [Sankalp](https://github.com/S4NKALP)

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/S4NKALP)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/sankalp)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/sankalp)

</div>
