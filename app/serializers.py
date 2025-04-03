import django.db
from rest_framework import serializers
from .models import (
    Attendance, AttendanceRecord, Batch, Course, FCMDevice, Institute,
    Notice, Routine, Staff, Student, Subject, Staff_leave, Student_Leave,
    StudentFeedback, InstituteFeedback, StaffInstituteFeedback, CourseTracking,
    TOTPSecret, ResetToken
)

class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ['id', 'token']

class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = ['id', 'name', 'phone', 'email', 'address', 'pan_no', 'reg_no', 'logo', 'description']

class SubjectSerializer(serializers.ModelSerializer):
    syllabus_pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'course', 'semester_or_year', 'syllabus_pdf', 'syllabus_pdf_url']

    def get_syllabus_pdf_url(self, obj):
        return obj.get_pdf_url()

class CourseSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'name', 'duration', 'duration_type', 'subjects']

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['id', 'name', 'start_date', 'end_date']

class StudentSerializer(serializers.ModelSerializer):
    batches = BatchSerializer(many=True, read_only=True)
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'name', 'status', 'gender', 'birth_date', 'email', 'phone',
            'temporary_address', 'permanent_address', 'marital_status', 'parent_name',
            'parent_phone', 'citizenship_no', 'image', 'batches', 'course',
            'current_semester', 'joining_date'
        ]
        read_only_fields = ['id']

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = [
            'id', 'name', 'gender', 'designation', 'birth_date', 'phone', 'email',
            'temporary_address', 'permanent_address', 'marital_status', 'parent_name',
            'parent_phone', 'citizenship_no', 'passport', 'image', 'joining_date',
            'is_active'
        ]
        read_only_fields = ['id']

class RoutineSerializer(serializers.ModelSerializer):
    teacher = StaffSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Routine
        fields = [
            'id', 'course', 'subject', 'teacher', 'start_time', 'end_time',
            'semester_or_year', 'is_active'
        ]

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = ['id', 'attendance', 'student', 'student_attend']

class AttendanceSerializer(serializers.ModelSerializer):
    records = AttendanceRecordSerializer(many=True, read_only=True)
    routine = RoutineSerializer(read_only=True)
    teacher = StaffSerializer(read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'date', 'routine', 'teacher', 'teacher_attend', 'class_status', 'records']

class NoticeSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = ['id', 'title', 'message', 'image', 'image_url', 'created_at']
        read_only_fields = ['created_at']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class StaffLeaveSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Staff_leave
        fields = ['id', 'staff', 'start_date', 'end_date', 'message', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class StudentLeaveSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Student_Leave
        fields = ['id', 'student', 'start_date', 'end_date', 'message', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class StudentFeedbackSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    teacher = StaffSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = StudentFeedback
        fields = ['id', 'student', 'teacher', 'rating', 'feedback_text', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class InstituteFeedbackSerializer(serializers.ModelSerializer):
    user = StudentSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = InstituteFeedback
        fields = [
            'id', 'institute', 'user', 'feedback_type', 'rating', 'feedback_text',
            'is_anonymous', 'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class StaffInstituteFeedbackSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = StaffInstituteFeedback
        fields = [
            'id', 'institute', 'staff', 'feedback_type', 'rating', 'feedback_text',
            'is_anonymous', 'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class CourseTrackingSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = CourseTracking
        fields = [
            'id', 'student', 'course', 'enrollment_date', 'start_date', 'expected_end_date',
            'actual_end_date', 'progress_status', 'completion_percentage', 'current_semester',
            'semester_start_date', 'semester_end_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'enrollment_date']

class TOTPSecretSerializer(serializers.ModelSerializer):
    class Meta:
        model = TOTPSecret
        fields = ['id', 'identifier', 'created_at', 'expires_at']

class ResetTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetToken
        fields = ['id', 'token', 'identifier', 'created_at', 'expires_at']

