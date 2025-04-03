from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from .models import Staff, Student

class MultiModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate the user based on username (email or phone) and password.
        """
        if username is None or password is None:
            return None
        
        # Try authenticating as Staff by phone
        # Use filter().first() to avoid MultipleObjectsReturned error
        staff = Staff.objects.filter(phone=username).first()
        if staff and staff.check_password(password):
            return staff

        # Try authenticating as Staff by email
        # Use filter().first() to avoid MultipleObjectsReturned error
        staff = Staff.objects.filter(email=username).first()
        if staff and staff.check_password(password):
            return staff

        # Try authenticating as Student by phone
        # Use filter().first() to avoid MultipleObjectsReturned error
        student = Student.objects.filter(phone=username).first()
        if student and student.check_password(password):
            return student

        # Try authenticating as Student by email
        # Use filter().first() to handle multiple students with same email
        student = Student.objects.filter(email=username).first()
        if student and student.check_password(password):
            return student

        # Return None if no match
        return None

    def get_user(self, user_id):
        """
        Retrieve a user instance using their ID.
        """
        for model in [Staff, Student]:
            try:
                return model.objects.get(pk=user_id)
            except model.DoesNotExist:
                continue
        return None

    def get_group_permissions(self, user_obj, obj=None):
        """
        Return a set of permission strings that the user has through their groups.
        """
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        
        if isinstance(user_obj, (Staff, Student)):
            if not hasattr(user_obj, '_group_perm_cache'):
                perms = set()
                for group in user_obj.groups.all():
                    perms.update(
                        "%s.%s" % (ct, name) 
                        for ct, name in group.permissions.values_list(
                            'content_type__app_label',
                            'codename'
                        )
                    )
                user_obj._group_perm_cache = perms
            return user_obj._group_perm_cache
        else:
            return super().get_group_permissions(user_obj, obj)

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        
        if isinstance(user_obj, (Staff, Student)):
            return self.get_group_permissions(user_obj, obj)
        else:
            return super().get_all_permissions(user_obj, obj)

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        
        if isinstance(user_obj, (Staff, Student)):
            return perm in self.get_all_permissions(user_obj, obj)
        else:
            return super().has_perm(user_obj, perm, obj)
