import django.db
from rest_framework import serializers
from .models import (Attendance, AttendanceRecord, Batch, Course, Expenses, FCMDevice, Fee,
    Institute, Routine, Salary, Staff, Student, StudentRoutine, Subtopic, Topic, Vendor)

class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ['id', 'token']
        depth = 10

class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        depth = 10
        fields = ['id', 'name', 'phone', 'email', 'address', 'pan_no', 'reg_no', 'logo', 'description']


class SubtopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtopic
        depth = 10 
        fields = ['id', 'name']


class TopicSerializer(serializers.ModelSerializer):
    subtopics = SubtopicSerializer(read_only=True, many=True).data
    class Meta:
        model = Topic
        fields = ['id', 'name', 'subtopics']
        depth = 10 


class CourseSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(read_only=True, many=True).data
    class Meta:
        model = Course
        depth = 3
        fields = ['id', 'name', 'amount', 'duration', 'duration_type', 'remarks', 'topics']



class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        depth = 10 
        fields = [
            'id', 'name', 'status', 'gender', 'birth_date', 'email', 'phone',
            'temporary_address', 'permanent_address', 'marital_status', 'parent_name',
            'parent_phone', 'citizenship_no', 'qualification', 'image', 'batches', 'courses',
            'subtotal', 'discount', 'total', 'paid', 'remaining', 'joining_date', 'file', 'remarks'
        ]



class BatchSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True).data
    class Meta:
        model = Batch
        depth = 10 
        fields = ['id', 'name', 'start_date', 'end_date', 'students']



class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = [
            'id', 'student', 'old_total', 'old_paid', 'old_remaining', 'balance_amount',
            'payment_date', 'payment_method', 'total', 'paid', 'remaining', 'remarks'
        ]
        depth = 10 

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        depth = 10 
        fields = ['id', 'name', 'address', 'phone']

class ExpensesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expenses
        depth = 10 
        fields = [
            'id', 'name', 'amount', 'date', 'vendor', 'paid', 'credit', 'credit_date', 'remarks'
        ]

class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        depth = 10
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):
    salaries = SalarySerializer(many=True).data
    class Meta:
        model = Staff
        depth = 10 
        fields = '__all__'
        # fields = [
        #     'id', 'name', 'gender', 'designation', 'birth_date', 'phone', 'email',
        #     'temporary_address', 'permanent_address', 'marital_status', 'parent_name',
        #     'parent_phone', 'citizenship_no', 'passport', 'image', 'monthly', 'pending_salary', 'remarks', 'salaries'
        # ]

class RoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routine
        depth = 10 
        fields = ['id', 'name', 'start_time', 'end_time', 'teacher']

class StudentRoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentRoutine
        depth = 10 
        fields = ['id', 'student', 'routine', 'course', 'course_status']


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        depth = 10 
        fields = ['id', 'attendance', 'student', 'student_attend']


class AttendanceSerializer(serializers.ModelSerializer):
    records = AttendanceRecordSerializer(many=True).data
    class Meta:
        model = Attendance
        depth = 1
        fields = ['id', 'date', 'routine', 'teacher', 'teacher_attend', 'class_status', 'records']

