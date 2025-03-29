# 📚 Student Management System (SMS)

<div align="center">

[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.1.7-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/S4NKALP/Student-Management-System-In-Django)](https://github.com/S4NKALP/Student-Management-System-In-Django/stargazers)
[![Arch Linux](https://img.shields.io/badge/Arch%20Linux-1793D1?logo=arch-linux&logoColor=white)](https://archlinux.org/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

A modern and comprehensive Student Management System built with Django.

</div>

## 💻 Tech Stack

<div align="center">

### 🔥 Core Technologies
| <img src="https://techstack-generator.vercel.app/python-icon.svg" alt="Python" width="100" height="100"/> | <img src="https://techstack-generator.vercel.app/django-icon.svg" alt="Django" width="100" height="100"/> | <img src="https://techstack-generator.vercel.app/js-icon.svg" alt="JavaScript" width="100" height="100"/> | <img src="https://techstack-generator.vercel.app/mysql-icon.svg" alt="MySQL" width="100" height="100"/> | <img src="https://techstack-generator.vercel.app/restapi-icon.svg" alt="REST API" width="100" height="100"/> |
|:---:|:---:|:---:|:---:|:---:|
| <b>Python</b> | <b>Django</b> | <b>JavaScript</b> | <b>MySQL</b> | <b>REST API</b> |

### ⚡ Additional Technologies
| <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/redis/redis-original-wordmark.svg" alt="Redis" width="80" height="80"/> | <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/nginx/nginx-original.svg" alt="Nginx" width="80" height="80"/> | <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/bootstrap/bootstrap-plain-wordmark.svg" alt="Bootstrap" width="80" height="80"/> | <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original-wordmark.svg" alt="HTML5" width="80" height="80"/> | <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original-wordmark.svg" alt="CSS3" width="80" height="80"/> | <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/git/git-original-wordmark.svg" alt="Git" width="80" height="80"/> |
|:---:|:---:|:---:|:---:|:---:|:---:|
| <b>Redis</b> | <b>Nginx</b> | <b>Bootstrap</b> | <b>HTML5</b> | <b>CSS3</b> | <b>Git</b> |

</div>

## 🖥️ Development Environment

- **Processor**: Intel Core i5-7300U
- **Operating System**: Arch Linux
- **Window Manager**: [Hyprland](https://github.com/S4NKALP/hyprland)
- **Status Bar**: [Modus](https://github.com/S4NKALP/Modus)
- **Editor**: [Neovim](https://github.com/S4NKALP/nvim)

## ✨ Key Features

<div align="center">

| Feature | Description |
|---------|-------------|
| 👥 Multi-User Roles | Admin, Staff, and Student interfaces |
| 📚 Course Management | Comprehensive course and subject tracking |
| 📊 Attendance System | Real-time attendance monitoring |
| 📝 Leave Management | Streamlined leave application process |
| 📢 Notice Board | Instant announcements and updates |
| 💬 Feedback System | Student and staff feedback collection |
| 🔐 OTP Verification | Secure authentication system |
| ☁️ Cloud Storage | Google Cloud integration |
| 🔥 Firebase | Real-time notifications and auth |

</div>

## 🚀 Quick Start

### Linux Users
```bash
# Clone & Setup
git clone https://github.com/S4NKALP/Student-Management-System-In-Django.git
cd Student-Management-System-In-Django
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env  # Edit with your settings

# Run
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Windows Users
```powershell
# Prerequisites
# Install Python from https://www.python.org/downloads/
# Install Git from https://git-scm.com/download/win
# Install Visual C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Clone & Setup
git clone https://github.com/S4NKALP/Student-Management-System-In-Django.git
cd Student-Management-System-In-Django
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Configure
copy .env.example .env
# Edit .env file with your settings

# Run
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### ⚠️ Common Issues (Windows)
- If `pip install` fails, make sure you have Visual C++ Build Tools installed
- If `python` command not found, add Python to your PATH environment variable
- If permission errors occur, run Command Prompt as Administrator
- If virtualenv fails, try: `python -m pip install --upgrade virtualenv`

### 🔐 Environment Variables (.env)
```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=sms_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# Email Configuration (for OTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# Firebase Configuration
FIREBASE_DATABASE_URL=your-firebase-url
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=your-cert-url

# Google Cloud Storage
GS_BUCKET_NAME=your-bucket-name
GS_CREDENTIALS=path/to/credentials.json
```

> **Note**: Never commit your `.env` file to version control. Keep your credentials secure!

## 🎯 Project Roadmap

<div align="center">

### ⚠️ Important Notice
```
This is a Minor Project created for educational purposes.
Features listed in the roadmap may or may not be implemented.
```

</div>

### 🎯 Current (v1.0)
- ✅ Core SMS functionality
- ✅ User management
- ✅ Course tracking
- ✅ Basic features

### 🔜 Upcoming (v1.1+)
- 👨‍👩‍👧‍👦 Parents dashboard
- 📚 Teacher study materials
- 📖 Library management
- 📊 Enhanced analytics
- 🤝 Parent-teacher meetings

## 📮 Support & Links

<div align="center">

[![GitHub Issues](https://img.shields.io/github/issues/S4NKALP/Student-Management-System-In-Django)](https://github.com/S4NKALP/Student-Management-System-In-Django/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/S4NKALP/Student-Management-System-In-Django)](https://github.com/S4NKALP/Student-Management-System-In-Django/pulls)
[![Documentation](https://img.shields.io/badge/docs-wiki-blue)](https://github.com/S4NKALP/Student-Management-System-In-Django/wiki)

</div>

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

## 📄 License

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

</div>

---

<div align="center">

### Made with ❤️ by [Sankalp](https://github.com/S4NKALP)

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/S4NKALP)
<!-- [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/sankalp)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/sankalp) -->

</div>
