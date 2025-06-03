# 🎓 Student Management System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)
[![Django](https://img.shields.io/badge/Django-Latest-green)](https://www.djangoproject.com)
[![License](https://img.shields.io/badge/License-GPL3.0-orange)](LICENSE)
[![Redis](https://img.shields.io/badge/Redis-Required-red)](https://redis.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supported-blue)](https://www.postgresql.org)

A comprehensive Django-based Student Management System with modern features and robust architecture. 🚀

## ✨ Features

- 🔐 User Authentication and Authorization
- 👨‍🎓 Student Information Management
- 📚 Course Management
- 📊 Attendance Tracking
- 📝 Grade Management
- 👨‍👩‍👧‍👦 Parent Portal
- 📱 Admin Dashboard
- 🔥 Firebase Integration
- 📱 SMS Notifications
- 📧 Email Notifications
- 💾 Caching System
- 🔒 Security Features
- 🎨 Responsive UI with Jazzmin Admin Theme

## 🛠️ Prerequisites

- Python 3.8 or higher
- Redis Server
- PostgreSQL (recommended) or SQLite
- Firebase Account (for Firebase features)
- SMS Gateway Account (for SMS features)

## 🔥 Firebase Setup

1. **Create a Firebase Project:**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Add project" and follow the setup wizard
   - Give your project a name and enable Google Analytics (optional)

2. **Get Firebase Configuration:**
   - In Firebase Console, click on the gear icon (⚙️) next to "Project Overview"
   - Select "Project settings"
   - Scroll down to "Your apps" section
   - Click the web icon (</>)
   - Register your app with a nickname
   - Copy the configuration object that looks like this:
   ```javascript
   const firebaseConfig = {
     apiKey: "xxx",
     authDomain: "xxx",
     projectId: "xxx",
     storageBucket: "xxx",
     messagingSenderId: "xxx",
     appId: "xxx",
     measurementId: "xxx"
   };
   ```

3. **Set up Firebase configuration files:**
   ```bash
   # Copy and rename the example files
   cp static/firebase-messaging-sw.example.js static/firebase-messaging-sw.js
   cp static/js/firebase-config.example.js static/js/firebase-config.js
   
   # Update the configuration in both files with your Firebase credentials
   # - In firebase-messaging-sw.js: Update the firebaseConfig object
   # - In firebase-config.js: Update both firebaseConfig and vapidKey
   ```

4. **Get Service Account Key:**
   - In Project Settings, go to "Service accounts" tab
   - Click "Generate new private key"
   - Save the downloaded JSON file as `firebase-key.json` in your project root
   - Add this file to `.gitignore` to keep it secure

5. **Update Environment Variables:**
   - Copy the values from your Firebase configuration to your `.env` file:
   ```env
   FIREBASE_API_KEY=your-api-key
   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   FIREBASE_MESSAGING_SENDER_ID=your-sender-id
   FIREBASE_APP_ID=your-app-id
   FIREBASE_MEASUREMENT_ID=your-measurement-id
   ```

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/S4NKALP/Student-Management-System-In-Django.git
   cd Student-Management-System-In-Django
   ```

2. **Choose your installation method:**

   **Using UV (Recommended, faster):**
   ```bash
   # Install UV if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # UV will automatically:
   # - Create and manage virtual environment
   # - Install all dependencies
   # - Handle package versions
   # - Optimize installation process
   ```

   **Using pip (Traditional method):**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root with the following variables:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=your-database-url

   # Email Configuration
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   DEFAULT_FROM_EMAIL=your-email@example.com
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   EMAIL_USE_TLS=True

   # Firebase Configuration
   FIREBASE_API_KEY=your-api-key
   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   FIREBASE_MESSAGING_SENDER_ID=your-sender-id
   FIREBASE_APP_ID=your-app-id
   FIREBASE_MEASUREMENT_ID=your-measurement-id

   # SMS Configuration
   SMS_API_KEY=your-sms-api-key
   SMS_SENDER_ID=your-sender-id
   ```

4. **Run migrations:**
   ```bash
   # Create database migrations
   python manage.py makemigrations

   # Apply migrations
   python manage.py migrate
   ```

5. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

## 🏃‍♂️ Running the Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000 to access the application.

## 🚀 Production Deployment

For production deployment, it's recommended to:

1. Set `DEBUG=False` in your environment variables
2. Use a production-grade database (PostgreSQL recommended)
3. Set up proper SSL/TLS certificates
4. Configure a production-grade web server (Nginx/Apache)
5. Use Gunicorn as the WSGI server:
   ```bash
   gunicorn student_management_system.wsgi:application
   ```

## 📁 Project Structure

```
student_management_system/
├── app/                    # Main application directory
├── static/                 # Static files (CSS, JS, images)
├── templates/             # HTML templates
├── student_management_system/  # Project settings
├── manage.py              # Django management script
├── requirements.txt       # Project dependencies
└── README.md             # This file
```

## 🔒 Security Features

- CSRF Protection
- XSS Protection
- SQL Injection Protection
- Secure Password Hashing
- Session Security
- HTTPS Enforcement
- Security Headers
- Rate Limiting

## 📚 API Endpoints

The system provides various AJAX endpoints for data exchange between the frontend and backend:

### 🔐 Authentication Endpoints
- `POST /login/` - User login
- `POST /logout/` - User logout
- `POST /password-reset/` - Password reset options
- `POST /password-reset/phone/` - Phone-based password reset
- `POST /password-reset/email/` - Email-based password reset
- `POST /password-reset/set/` - Set new password

### 📊 Dashboard Endpoints
- `GET /app/dashboard/` - Main dashboard
- `GET /app/student-dashboard/` - Student dashboard
- `GET /app/teacher-dashboard/` - Teacher dashboard
- `GET /app/parent-dashboard/` - Parent dashboard
- `GET /app/admission-officer-dashboard/` - Admission officer dashboard
- `GET /app/hodDashboard/` - HOD dashboard

### 👨‍🎓 Student Management
- `GET /app/get-students/` - Get all students
- `GET /app/get-student/<int:student_id>/` - Get student details
- `POST /app/add-student/` - Add new student
- `PUT /app/edit-student/<int:student_id>/` - Edit student
- `DELETE /app/delete-student/<int:student_id>/` - Delete student

### 📚 Course and Subject Management
- `GET /app/get-subjects/` - Get all subjects
- `GET /app/get-courses/` - Get all courses
- `POST /app/add-subject/` - Add new subject
- `PUT /app/edit-subject/<int:subject_id>/` - Edit subject
- `DELETE /app/delete-subject/<int:subject_id>/` - Delete subject
- `GET /app/get-course-duration/` - Get course duration
- `GET /app/get-subject-schedule/` - Get subject schedule

### 👨‍🏫 Staff Management
- `GET /app/get-teachers/` - Get all teachers
- `POST /app/add-staff/` - Add new staff
- `GET /app/staff/<int:staff_id>/` - Get staff details
- `PUT /app/edit-staff/<int:staff_id>/` - Edit staff
- `DELETE /app/delete-staff/<int:staff_id>/` - Delete staff

### 🤝 Meeting Management
- `GET /app/api/meetings/<int:meeting_id>/` - Get meeting details
- `POST /app/api/meetings/add/` - Create new meeting
- `PUT /app/api/meetings/<int:meeting_id>/edit/` - Update meeting
- `POST /app/api/meetings/<int:meeting_id>/cancel/` - Cancel meeting
- `GET /app/api/meetings/<int:meeting_id>/notes/` - Get meeting notes
- `GET /app/api/meetings/<int:meeting_id>/agenda/` - Get meeting agenda

### 📅 Routine Management
- `GET /app/api/hod/routines/<int:routine_id>/` - Get routine details
- `POST /app/api/hod/routines/` - Create new routine
- `PUT /app/api/hod/routines/<int:routine_id>/edit/` - Update routine
- `DELETE /app/api/hod/routines/<int:routine_id>/delete/` - Delete routine

### 📝 Leave Management
- `POST /app/request-leave/` - Request student leave
- `POST /app/request-staff-leave/` - Request staff leave
- `POST /app/approve-student-leave/<int:leave_id>/` - Approve student leave
- `POST /app/approve-staff-leave/<int:leave_id>/` - Approve staff leave
- `POST /app/reject-student-leave/<int:leave_id>/` - Reject student leave
- `POST /app/reject-staff-leave/<int:leave_id>/` - Reject staff leave
- `GET /app/get-student-leaves/` - Get student leaves
- `GET /app/get-staff-leaves/` - Get staff leaves

### 💬 Feedback Management
- `POST /app/submit-feedback/` - Submit student feedback
- `POST /app/submit-institute-feedback/` - Submit institute feedback
- `POST /app/submit-staff-institute-feedback/` - Submit staff institute feedback
- `POST /app/parent/feedback/submit/` - Submit parent feedback
- `POST /app/parent/feedback/institute/submit/` - Submit parent institute feedback

### 👤 Profile Management
- `POST /app/update-profile/` - Update user profile
- `POST /app/change-password/` - Change password
- `POST /app/teacher-update-profile-picture/` - Update teacher profile picture
- `POST /app/teacher-change-password/` - Change teacher password

### 🔥 Firebase Integration
- `POST /app/saveFCMToken/` - Save Firebase Cloud Messaging token
- `GET /firebase-messaging-sw.js` - Firebase service worker

### 📢 Notice Management
- `POST /app/add-notice/` - Add new notice
- `DELETE /app/delete-notice/<int:notice_id>/` - Delete notice
- `POST /app/hod/add-notice/` - Add HOD notice
- `GET /app/notice/<int:notice_id>/` - View notice

### 📊 Attendance Management
- `POST /app/save-attendance/` - Save attendance
- `GET /app/get-attendance-form/` - Get attendance form

### 📈 Progress Tracking
- `GET /app/api/get-student-progress/` - Get student progress
- `GET /app/api/get-progress/<int:progress_id>/` - Get specific progress
- `PUT /app/api/edit-progress/<int:progress_id>/` - Edit progress

## 📄 License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0) - see the LICENSE file for details.

## 💬 Support

For support, please open an issue in the GitHub repository or contact the maintainers.