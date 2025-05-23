JAZZMIN_SETTINGS = {
    "site_title": "Student Management System",
    "site_header": "Student Management",
    "site_brand": "SMS",
    "site_logo": "img/logo.png",
    "login_logo": "img/logo.png",
    "login_logo_dark": None,
    "site_logo_classes": "img-circle",
    "login_logo_classes": "",
    "custom_css": "css/custom.css",
    "welcome_sign": "Welcome to Student Management System",
    "copyright": "Student Management System",
    "search_model": ["app.Student", "app.Staff", "app.Course"],
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "auth.User"},
    ],
    "usermenu_links": [{"model": "auth.user"}],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "dashboard",
        "authentication",
        "organization",
        "human_managementorganization.institute",
        "organization.batch",
        "organization.course",
        "human_management.student",
        "human_management.staff",
        "human_management.routine",
        "human_management.staff_leave",
        "human_management.student_leave",
        "human_management.studentfeedback",
        "human_management.coursetracking",
        "human_management.attendance",
        "human_management.institutefeedback",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "app.student": "fas fa-user-graduate",
        "app.staff": "fas fa-chalkboard-teacher",
        "app.course": "fas fa-book",
        "app.subject": "fas fa-book-open",
        "app.attendance": "fas fa-calendar-check",
        "app.studentfeedback": "fas fa-comment",
        "app.institutefeedback": "fas fa-comments",
        "app.student_leave": "fas fa-calendar-times",
        "app.staff_leave": "fas fa-calendar-minus",
        "app.notice": "fas fa-bullhorn",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_js": None,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
