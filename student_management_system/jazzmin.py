JAZZMIN_SETTINGS = {
    "site_title": "Student Management System Admin",
    "site_header": "Student Management System",
    "site_brand": "SMS",
    "site_logo": "/dist/img/logo.png",
    "site_logo_classes": "img-circle",
    "site_icon": "/dist/img/logo.png",
    "welcome_sign": "Welcome to the Student Management System",
    "copyright": "ADDRSSS",
    ############
    # Top Menu #
    ############
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Dashboard", "url": "dashboard", "permissions": ["auth.view_user"]},
    ],
    #############
    # Side Menu #
    #############
    "show_sidebar": True,
    "navigation_expanded": True,
    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth", "dashboard", "app"],
    "custom_links": {
        "app": [
            {
                "name": "Dashboard",
                "url": "dashboard",
                "icon": "fas fa-tachometer-alt",
            },
        ],
    },


    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "app.student": "fas fa-user-graduate",
        "app.teacher": "fas fa-chalkboard-teacher",
        "app.course": "fas fa-book",
        "app.subject": "fas fa-book-open",
        "app.academicyear": "fas fa-calendar",
        "app.attendance": "fas fa-calendar-check",
        "app.attendancereport": "fas fa-clipboard-list",
        "app.leavereportstudent": "fas fa-user-clock",
        "app.leavereportteacher": "fas fa-clock",
        "app.feedbackstudent": "fas fa-comment-alt",
        "app.feedbackteacher": "fas fa-comments",
    },
}

JAZZMIN_UI_TWEAKS = {
    "theme": "lumen",
    # "dark_mode_theme": "cyborg",
}
