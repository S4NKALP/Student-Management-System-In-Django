JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Student Management System Admin",
    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Student Management System",
    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "SMS",
    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "/src/img/logo.png",
    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",
    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": None,
    # Welcome text on the login screen
    "welcome_sign": "Welcome to the Student Management System",
    # Copyright on the footer
    "copyright": "ADDRSSS",
    # theme
    # The model admin to search from the search bar, search bar omitted if excluded
    # "search_model": "auth.User",
    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,
    "version": False,
    ############
    # Top Menu #
    ############
    # Links to put along the top menu
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        # external url that opens in a new window (Permissions can be added)
        # {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        # model admin to link to (Permissions checked against model)
        # {"model": "auth.User"},
        # App with dropdown menu to all its models pages (Permissions checked against models)
        # {"app": "books"},
    ],
    #############
    # User Menu #
    #############
    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    # "usermenu_links": [
    #     {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
    #     {"model": "auth.user"}
    # ],
    #
    #############
    # Side Menu #
    #############
    # Whether to display the side menu
    "show_sidebar": True,
    # Whether to aut expand the menu
    "navigation_expanded": True,
    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],
    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],
    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth", "dashboard", "course"],
    "custom_links": {
        "courses": [
            {"name": "Manage Courses", "url": "add_course", "icon": "fas fa-book"}
        ],
        "menu": [
            {
                "name": "Dashboard",
                "url": "admin:index",
                "icon": "fas fa-tachometer-alt",
            },
            {
                "name": "Courses",
                "icon": "fas fa-book",
                "children": [
                    {
                        "name": "Manage Courses",
                        "url": "add_course",
                        "icon": "fas fa-plus",
                    },
                    {"name": "Course List", "model": "app.course"},
                ],
            },
            {"name": "Students", "icon": "fas fa-users", "models": ["app.student"]},
            {
                "name": "Teachers",
                "icon": "fas fa-chalkboard-teacher",
                "models": ["app.teacher"],
            },
            {"name": "Staff", "icon": "fas fa-user-tie", "models": ["app.staff"]},
            {
                "name": "Academics",
                "icon": "fas fa-graduation-cap",
                "children": [
                    {"model": "app.subject"},
                    {"model": "app.academicyear"},
                    {"model": "app.result"},
                    {"model": "app.attendance"},
                ],
            },
            {
                "name": "Library",
                "icon": "fas fa-book-reader",
                "models": ["app.library"],
            },
            {
                "name": "Certificates",
                "icon": "fas fa-certificate",
                "models": ["app.certificate"],
            },
            {
                "name": "News & Events",
                "icon": "fas fa-newspaper",
                "models": ["app.newsevent"],
            },
        ],
        "app": [
            {
                "name": "Dashboard",
                "url": "dashboard",
                "icon": "fas fa-tachometer-alt",
            },
            # {
            #     "name": "course",
            #     "url": "add_course",
            # },
        ],
    },
    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,
    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,
    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {
        "auth.user": "horizontal_tabs",
        "auth.group": "vertical_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    # "footer_fixed": True,
    "theme": "lumen",
    # "dark_mode_theme": "cyborg",
}
