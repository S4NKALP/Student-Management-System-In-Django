# Standard library imports
import django.db

# Third-party app imports
from rest_framework import serializers

# Local app imports
from app.firebase import FCMDevice
from app.models import (
    Attendance,
    AttendanceRecord,
    Batch,
    Course,
    CourseTracking,
    Institute,
    InstituteFeedback,
    Notice,
    Parent,
    ParentFeedback,
    ParentInstituteFeedback,
    Routine,
    Staff,
    StaffInstituteFeedback,
    StaffLeave,
    Student,
    StudentFeedback,
    StudentLeave,
    Subject,
    SubjectFile,
    TeacherParentMeeting,
    TOTPSecret,
    ResetToken,
)


class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ["id", "token"]


class InstituteSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Institute
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "address",
            "pan_no",
            "reg_no",
            "logo",
            "logo_url",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        return None


class BatchSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Batch
        fields = [
            "id",
            "name",
            "year",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CourseSerializer(serializers.ModelSerializer):
    subjects = serializers.SerializerMethodField()
    batches = BatchSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "code",
            "duration",
            "duration_type",
            "description",
            "is_active",
            "subjects",
            "batches",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_subjects(self, obj):
        from app.serializers import SubjectSerializer
        subjects = obj.subjects.all()
        return SubjectSerializer(subjects, many=True).data


class SubjectSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    syllabus_pdf_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "code",
            "course",
            "period_or_year",
            "syllabus_pdf",
            "syllabus_pdf_url",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_syllabus_pdf_url(self, obj):
        if obj.syllabus_pdf:
            return obj.syllabus_pdf.url
        return None


class StudentSerializer(serializers.ModelSerializer):
    batches = BatchSerializer(many=True, read_only=True)
    course = CourseSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "name",
            "status",
            "gender",
            "birth_date",
            "email",
            "phone",
            "temporary_address",
            "permanent_address",
            "marital_status",
            "parent_name",
            "parent_phone",
            "citizenship_no",
            "image",
            "image_url",
            "batches",
            "course",
            "current_period",
            "joining_date",
            "fcm_token",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class StaffSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Staff
        fields = [
            "id",
            "name",
            "gender",
            "designation",
            "birth_date",
            "phone",
            "email",
            "temporary_address",
            "permanent_address",
            "marital_status",
            "parent_name",
            "parent_phone",
            "citizenship_no",
            "passport",
            "image",
            "image_url",
            "joining_date",
            "is_active",
            "fcm_token",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class RoutineSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    teacher = StaffSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Routine
        fields = [
            "id",
            "course",
            "subject",
            "teacher",
            "start_time",
            "end_time",
            "period_or_year",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AttendanceSerializer(serializers.ModelSerializer):
    routine = RoutineSerializer(read_only=True)
    teacher = StaffSerializer(read_only=True)
    records = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "date",
            "routine",
            "teacher",
            "teacher_attend",
            "class_status",
            "records",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_records(self, obj):
        from app.serializers import AttendanceRecordSerializer
        records = obj.records.all()
        return AttendanceRecordSerializer(records, many=True).data


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "attendance",
            "student",
            "student_attend",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NoticeSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "image",
            "image_url",
            "message",
            "file",
            "file_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None


class StaffLeaveSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = StaffLeave
        fields = [
            "id",
            "staff",
            "start_date",
            "end_date",
            "message",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentLeaveSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = StudentLeave
        fields = [
            "id",
            "student",
            "start_date",
            "end_date",
            "message",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentFeedbackSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    teacher = StaffSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = StudentFeedback
        fields = [
            "id",
            "student",
            "teacher",
            "rating",
            "feedback_text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ParentFeedbackSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()
    teacher = StaffSerializer(read_only=True)
    student = StudentSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ParentFeedback
        fields = [
            "id",
            "parent",
            "teacher",
            "student",
            "rating",
            "feedback_text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_parent(self, obj):
        from app.serializers import ParentSerializer
        return ParentSerializer(obj.parent).data


class InstituteFeedbackSerializer(serializers.ModelSerializer):
    institute = InstituteSerializer(read_only=True)
    user = StudentSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = InstituteFeedback
        fields = [
            "id",
            "institute",
            "user",
            "feedback_type",
            "rating",
            "feedback_text",
            "is_anonymous",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StaffInstituteFeedbackSerializer(serializers.ModelSerializer):
    institute = InstituteSerializer(read_only=True)
    staff = StaffSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = StaffInstituteFeedback
        fields = [
            "id",
            "institute",
            "staff",
            "feedback_type",
            "rating",
            "feedback_text",
            "is_anonymous",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ParentInstituteFeedbackSerializer(serializers.ModelSerializer):
    institute = InstituteSerializer(read_only=True)
    parent = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ParentInstituteFeedback
        fields = [
            "id",
            "institute",
            "parent",
            "feedback_type",
            "rating",
            "feedback_text",
            "is_anonymous",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_parent(self, obj):
        from app.serializers import ParentSerializer
        return ParentSerializer(obj.parent).data


class CourseTrackingSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    current_period_display = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = CourseTracking
        fields = [
            "id",
            "student",
            "course",
            "enrollment_date",
            "start_date",
            "expected_end_date",
            "actual_end_date",
            "progress_status",
            "completion_percentage",
            "current_period",
            "current_period_display",
            "period_start_date",
            "period_end_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "current_period_display"]


class SubjectFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    uploaded_by = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = SubjectFile
        fields = [
            "id",
            "subject",
            "title",
            "description",
            "file",
            "file_url",
            "uploaded_by",
            "uploaded_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "uploaded_at"]

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None

    def get_uploaded_by(self, obj):
        from app.serializers import StaffSerializer
        if obj.uploaded_by:
            return StaffSerializer(obj.uploaded_by).data
        return None


class TOTPSecretSerializer(serializers.ModelSerializer):
    class Meta:
        model = TOTPSecret
        fields = ["id", "identifier", "secret_key", "created_at", "expires_at"]
        read_only_fields = ["id", "created_at"]


class ResetTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetToken
        fields = ["id", "token", "identifier", "created_at", "expires_at"]
        read_only_fields = ["id", "created_at"]


class ParentSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Parent
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "address",
            "students",
            "image",
            "image_url",
            "fcm_token",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
