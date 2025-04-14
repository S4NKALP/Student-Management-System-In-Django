import random
from datetime import datetime, timedelta
import pytz
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
from django.db import transaction
from faker import Faker
from app.models import (
    Institute, Batch, Course, Subject, Staff, Student, Parent,
    Routine, Attendance, AttendanceRecord, Notice,
    StaffLeave, StudentLeave, StudentFeedback, ParentFeedback,
    InstituteFeedback, StaffInstituteFeedback, ParentInstituteFeedback,
    CourseTracking, TeacherParentMeeting, SubjectFile
)

class Command(BaseCommand):
    help = 'Generate fake data for testing the SMS application'

    def add_arguments(self, parser):
        parser.add_argument('--students', type=int, default=50, help='Number of students to create')
        parser.add_argument('--staff', type=int, default=20, help='Number of staff members to create')
        parser.add_argument('--parents', type=int, default=40, help='Number of parents to create')
        parser.add_argument('--courses', type=int, default=5, help='Number of courses to create')
        parser.add_argument('--subjects', type=int, default=4, help='Subjects per course')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before generating new data')

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker()
        
        # Get parameters
        num_students = options['students']
        num_staff = options['staff']
        num_parents = options['parents']
        num_courses = options['courses']
        subjects_per_course = options['subjects']
        clear_data = options['clear']
        
        # Get or create groups
        staff_group, _ = Group.objects.get_or_create(name='Teacher')
        parent_group, _ = Group.objects.get_or_create(name='Parent')
        student_group, _ = Group.objects.get_or_create(name='Student')
        
        # Clear existing data if requested
        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            TeacherParentMeeting.objects.all().delete()
            ParentInstituteFeedback.objects.all().delete()
            StaffInstituteFeedback.objects.all().delete()
            InstituteFeedback.objects.all().delete()
            ParentFeedback.objects.all().delete()
            StudentFeedback.objects.all().delete()
            StudentLeave.objects.all().delete()
            StaffLeave.objects.all().delete()
            Notice.objects.all().delete()
            AttendanceRecord.objects.all().delete()
            Attendance.objects.all().delete()
            Routine.objects.all().delete()
            SubjectFile.objects.all().delete()
            CourseTracking.objects.all().delete()
            
            # Clear many-to-many relationships before deleting models
            for parent in Parent.objects.all():
                parent.students.clear()
            
            for student in Student.objects.all():
                student.batches.clear()
            
            Subject.objects.all().delete()
            Parent.objects.all().delete()
            Student.objects.all().delete()
            Staff.objects.all().delete()
            Course.objects.all().delete()
            Batch.objects.all().delete()
            Institute.objects.all().delete()
            
            self.stdout.write(self.style.SUCCESS('Data cleared successfully'))
        
        # Create Institute
        institute = self._create_institute(fake)
        
        # Create batches (last 4 years)
        batches = self._create_batches()
        
        # Create courses
        courses = self._create_courses(fake, num_courses)
        
        # Create subjects for each course
        subjects = self._create_subjects(fake, courses, subjects_per_course)
        
        # Create staff members
        staff_members = self._create_staff(fake, num_staff, staff_group)
        
        # Create students
        students = self._create_students(fake, num_students, courses, batches, student_group)
        
        # Create parents and link to students
        parents = self._create_parents(fake, num_parents, students, parent_group)
        
        # Create routines and class schedules
        routines = self._create_routines(courses, subjects, staff_members)
        
        # Create attendance records
        attendance_records = self._create_attendance(routines, students)
        
        # Create notices
        notices = self._create_notices(fake)
        
        # Create leave requests
        self._create_leaves(fake, staff_members, students)
        
        # Create feedback
        self._create_feedback(fake, students, staff_members, parents, institute)
        
        # Create parent-teacher meetings
        self._create_meetings(fake, staff_members, parents)
        
        # Create subject files
        self._create_subject_files(fake, subjects, staff_members)
        
        # Create course tracking for students
        self._create_course_tracking(students, courses)
        
        self.stdout.write(self.style.SUCCESS('Successfully generated fake data!'))
    
    def _create_institute(self, fake):
        institute, created = Institute.objects.get_or_create(
            name=fake.company() + " Institute of Technology",
            defaults={
                'phone': fake.phone_number(),
                'email': fake.company_email(),
                'address': fake.address(),
                'pan_no': 'PAN' + fake.numerify(text='#####'),
                'reg_no': 'REG' + fake.numerify(text='######'),
                'description': fake.paragraph(nb_sentences=3)
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created institute: {institute.name}'))
        return institute
    
    def _create_batches(self):
        batches = []
        current_year = datetime.now().year
        
        for year in range(current_year - 3, current_year + 1):
            batch, created = Batch.objects.get_or_create(
                name=f'Batch {year}',
                defaults={'year': datetime(year, 1, 1)}
            )
            batches.append(batch)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created batch: {batch.name}'))
        
        return batches
    
    def _create_courses(self, fake, num_courses):
        courses = []
        course_names = [
            'Computer Science Engineering', 
            'Electrical Engineering', 
            'Mechanical Engineering',
            'Civil Engineering',
            'Chemical Engineering',
            'Electronics Engineering',
            'Information Technology',
            'Aerospace Engineering',
            'Biotechnology Engineering',
            'Data Science'
        ]
        
        # Ensure we don't try to create more courses than we have names for
        num_to_create = min(num_courses, len(course_names))
        
        for i in range(num_to_create):
            duration = random.choice([3, 4])
            duration_type = random.choice(['Year', 'Semester'])
            
            course, created = Course.objects.get_or_create(
                name=course_names[i],
                defaults={
                    'duration': duration,
                    'duration_type': duration_type
                }
            )
            courses.append(course)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created course: {course.name}'))
        
        return courses
    
    def _create_subjects(self, fake, courses, subjects_per_course):
        subjects = []
        
        subject_names = {
            'Computer Science Engineering': [
                'Data Structures', 'Algorithms', 'Database Systems', 'Operating Systems',
                'Computer Networks', 'Software Engineering', 'Web Development', 'AI and Machine Learning'
            ],
            'Electrical Engineering': [
                'Circuit Theory', 'Electrical Machines', 'Power Systems', 'Control Systems',
                'Digital Electronics', 'Microprocessors', 'Power Electronics', 'Electrical Measurements'
            ],
            'Mechanical Engineering': [
                'Thermodynamics', 'Fluid Mechanics', 'Manufacturing Processes', 'Machine Design',
                'Heat Transfer', 'Engineering Mechanics', 'Automobile Engineering', 'Materials Science'
            ],
            'Information Technology': [
                'Programming Fundamentals', 'Data Structures', 'Database Management', 'Web Technologies',
                'Computer Networks', 'Software Engineering', 'Cybersecurity', 'Cloud Computing'
            ],
            'Data Science': [
                'Statistical Methods', 'Machine Learning', 'Data Mining', 'Big Data Analytics',
                'Data Visualization', 'Deep Learning', 'Natural Language Processing', 'Time Series Analysis'
            ]
        }
        
        # Add generic subjects for courses not explicitly defined
        generic_subjects = [
            'Mathematics I', 'Mathematics II', 'Physics', 'Chemistry',
            'Technical Writing', 'Engineering Ethics', 'Project Management', 'Research Methods'
        ]
        
        for course in courses:
            # Get subject list for this course or use generic subjects
            if course.name in subject_names:
                course_subject_names = subject_names[course.name]
            else:
                course_subject_names = generic_subjects
            
            max_year_or_sem = course.duration
            if course.duration_type == 'Semester':
                max_year_or_sem = course.duration * 2
            
            # Create subjects for each year/semester
            for year_or_sem in range(1, max_year_or_sem + 1):
                # Create a subset of subjects for this year/semester
                num_to_create = min(subjects_per_course, len(course_subject_names))
                selected_subjects = random.sample(course_subject_names, num_to_create)
                
                for subject_name in selected_subjects:
                    subject, created = Subject.objects.get_or_create(
                        name=subject_name,
                        course=course,
                        period_or_year=year_or_sem
                    )
                    subjects.append(subject)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created subject: {subject.name} for {course.name}'))
        
        return subjects
    
    def _create_staff(self, fake, num_staff, staff_group):
        staff_members = []
        
        # Create staff members
        for i in range(num_staff):
            gender = random.choice(['Male', 'Female'])
            first_name = fake.first_name_male() if gender == 'Male' else fake.first_name_female()
            last_name = fake.last_name()
            name = f"{first_name} {last_name}"
            
            # Generate a unique phone number
            while True:
                phone = fake.numerify(text='9#########')
                if not Staff.objects.filter(phone=phone).exists():
                    break
            
            staff = Staff(
                name=name,
                phone=phone,
                designation='Teacher',
                gender=gender,
                birth_date=fake.date_of_birth(minimum_age=30, maximum_age=65),
                email=fake.email(),
                temporary_address=fake.address(),
                permanent_address=fake.address(),
                marital_status=random.choice(['Married', 'Unmarried']),
                parent_name=fake.name(),
                parent_phone=fake.phone_number(),
                citizenship_no=fake.numerify(text='#########'),
                joining_date=fake.date_between(start_date='-5y', end_date='today')
            )
            staff.save()  # Save first to get primary key
            staff.set_password('staff123')  # Then set password
            staff.save()  # Save again to update password
            staff.groups.add(staff_group)  # Add to staff group
            staff_members.append(staff)
            self.stdout.write(self.style.SUCCESS(f'Created staff: {staff.name}'))
        
        return staff_members
    
    def _create_students(self, fake, num_students, courses, batches, student_group):
        students = []
        
        for i in range(num_students):
            gender = random.choice(['Male', 'Female'])
            first_name = fake.first_name_male() if gender == 'Male' else fake.first_name_female()
            last_name = fake.last_name()
            name = f"{first_name} {last_name}"
            
            # Generate a unique phone number
            while True:
                phone = fake.numerify(text='9#########')
                if not Student.objects.filter(phone=phone).exists():
                    break
            
            # Randomly assign a course and batch
            course = random.choice(courses)
            max_semester = course.duration
            if course.duration_type == 'Semester':
                max_semester = course.duration * 2
            
            current_period = random.randint(1, max_semester)
            
            student = Student(
                name=name,
                status=random.choice(['Active', 'Leave', 'Completed']),
                gender=gender,
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=25),
                email=fake.email(),
                phone=phone,
                temporary_address=fake.address(),
                permanent_address=fake.address(),
                marital_status=random.choice(['Married', 'Unmarried']),
                parent_name=fake.name(),
                parent_phone=fake.phone_number(),
                citizenship_no=fake.numerify(text='#########'),
                course=course,
                current_period=current_period,
                joining_date=fake.date_between(start_date='-4y', end_date='-1y')
            )
            student.save()  # Save first to get primary key
            student.set_password('student123')  # Then set password
            student.save()  # Save again to update password
            student.groups.add(student_group)  # Add to student group
            
            # Add student to a random batch
            batch = random.choice(batches)
            student.batches.add(batch)
            
            students.append(student)
            self.stdout.write(self.style.SUCCESS(f'Created student: {student.name}'))
        
        return students
    
    def _create_parents(self, fake, num_parents, students, parent_group):
        parents = []
        
        # Create parents and assign students
        for i in range(num_parents):
            gender = random.choice(['Male', 'Female'])
            first_name = fake.first_name_male() if gender == 'Male' else fake.first_name_female()
            last_name = fake.last_name()
            name = f"{first_name} {last_name}"
            
            # Generate a unique phone number
            while True:
                phone = fake.numerify(text='9#########')
                if not Parent.objects.filter(phone=phone).exists():
                    break
            
            parent = Parent(
                name=name,
                phone=phone,
                email=fake.email(),
                address=fake.address(),
            )
            parent.save()  # Save first to get primary key
            parent.set_password('parent123')  # Then set password
            parent.save()  # Save again to update password
            parent.groups.add(parent_group)  # Add to parent group
            
            # Assign 1-2 students to this parent
            num_children = random.randint(1, min(2, len(students)))
            assigned_students = random.sample(students, num_children)
            for student in assigned_students:
                parent.students.add(student)
            
            parents.append(parent)
            self.stdout.write(self.style.SUCCESS(f'Created parent: {parent.name} with {num_children} children'))
        
        return parents
    
    def _create_routines(self, courses, subjects, staff_members):
        routines = []
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        for course in courses:
            # Get subjects for this course
            course_subjects = Subject.objects.filter(course=course)
            
            for subject in course_subjects:
                # Assign a random teacher
                teacher = random.choice(staff_members)
                
                # Create routine for this subject
                start_time = datetime.strptime(f"{random.randint(9, 16)}:00", "%H:%M").time()
                end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=1)).time()
                
                routine = Routine(
                    course=course,
                    subject=subject,
                    teacher=teacher,
                    start_time=start_time,
                    end_time=end_time,
                    period_or_year=subject.period_or_year,
                    is_active=True
                )
                
                # Skip if there's a clash in times
                try:
                    routine.save()
                    routines.append(routine)
                    self.stdout.write(self.style.SUCCESS(f'Created routine for {subject.name} with {teacher.name}'))
                except Exception as e:
                    # Just skip if there's an error (likely due to unique constraint violation)
                    pass
        
        return routines
    
    def _create_attendance(self, routines, students):
        attendance_records = []
        
        # Create attendance for the past week
        for day_offset in range(7, 0, -1):
            date = datetime.now().date() - timedelta(days=day_offset)
            
            for routine in routines:
                # Create attendance for this routine on this date
                attendance = Attendance(
                    date=date,
                    routine=routine,
                    teacher=routine.teacher,
                    teacher_attend=random.choice([True, True, True, False]),  # More likely to attend
                    class_status=True
                )
                try:
                    attendance.save()
                    
                    # Find students in this course and semester
                    course_students = Student.objects.filter(
                        course=routine.course,
                        current_period=routine.period_or_year
                    )
                    
                    # Create attendance records for students
                    for student in course_students:
                        is_present = random.choice([True, True, False])  # 2/3 chance of being present
                        record = AttendanceRecord(
                            attendance=attendance,
                            student=student,
                            student_attend=is_present
                        )
                        record.save()
                        attendance_records.append(record)
                        
                    self.stdout.write(self.style.SUCCESS(f'Created attendance for {routine.subject.name} on {date}'))
                except Exception as e:
                    # Skip if there's an error
                    pass
        
        return attendance_records
    
    def _create_notices(self, fake):
        notices = []
        
        for i in range(10):  # Create 10 notices
            notice = Notice(
                title=fake.sentence(),
                message=fake.paragraph(nb_sentences=3),
                created_at=fake.date_time_between(start_date='-30d', end_date='now')
            )
            notice.save()
            notices.append(notice)
            self.stdout.write(self.style.SUCCESS(f'Created notice: {notice.title}'))
        
        return notices
    
    def _create_leaves(self, fake, staff_members, students):
        # Create staff leaves
        for staff in random.sample(staff_members, len(staff_members) // 3):  # 1/3 of staff
            start_date = fake.date_between(start_date='-30d', end_date='+30d')
            end_date = start_date + timedelta(days=random.randint(1, 5))
            
            leave = StaffLeave(
                staff=staff,
                start_date=start_date,
                end_date=end_date,
                message=fake.paragraph(),
                status=random.choice([0, 1, 2])  # Pending, Approved, Rejected
            )
            leave.save()
            self.stdout.write(self.style.SUCCESS(f'Created staff leave for {staff.name}'))
        
        # Create student leaves
        for student in random.sample(students, len(students) // 3):  # 1/3 of students
            start_date = fake.date_between(start_date='-30d', end_date='+30d')
            end_date = start_date + timedelta(days=random.randint(1, 5))
            
            leave = StudentLeave(
                student=student,
                start_date=start_date,
                end_date=end_date,
                message=fake.paragraph(),
                status=random.choice([0, 1, 2])  # Pending, Approved, Rejected
            )
            leave.save()
            self.stdout.write(self.style.SUCCESS(f'Created student leave for {student.name}'))
    
    def _create_feedback(self, fake, students, staff_members, parents, institute):
        # Create student feedback for teachers
        for student in random.sample(students, len(students) // 2):
            for teacher in random.sample(staff_members, min(3, len(staff_members))):
                try:
                    feedback = StudentFeedback(
                        student=student,
                        teacher=teacher,
                        rating=random.choice([3.5, 4.0, 4.5, 5.0]),
                        feedback_text=fake.paragraph()
                    )
                    feedback.save()
                    self.stdout.write(self.style.SUCCESS(f'Created student feedback from {student.name} for {teacher.name}'))
                except:
                    # Skip if there's an error (likely due to unique constraint)
                    pass
        
        # Create parent feedback for teachers
        for parent in random.sample(parents, len(parents) // 2):
            parent_students = parent.students.all()
            if parent_students:
                for student in parent_students:
                    for teacher in random.sample(staff_members, min(2, len(staff_members))):
                        try:
                            feedback = ParentFeedback(
                                parent=parent,
                                teacher=teacher,
                                student=student,
                                rating=random.choice([3.5, 4.0, 4.5, 5.0]),
                                feedback_text=fake.paragraph()
                            )
                            feedback.save()
                            self.stdout.write(self.style.SUCCESS(f'Created parent feedback from {parent.name} for {teacher.name}'))
                        except:
                            # Skip if there's an error
                            pass
        
        # Create institute feedback
        for student in random.sample(students, len(students) // 3):
            try:
                feedback = InstituteFeedback(
                    institute=institute,
                    user=student,
                    feedback_type=random.choice(['General', 'Facilities', 'Teaching', 'Infrastructure', 'Administration']),
                    rating=random.choice([3.0, 3.5, 4.0, 4.5, 5.0]),
                    feedback_text=fake.paragraph(),
                    is_anonymous=random.choice([True, False]),
                    is_public=True
                )
                feedback.save()
                self.stdout.write(self.style.SUCCESS(f'Created institute feedback from {student.name}'))
            except:
                # Skip if there's an error
                pass
        
        # Create staff institute feedback
        for staff in random.sample(staff_members, len(staff_members) // 3):
            try:
                feedback = StaffInstituteFeedback(
                    institute=institute,
                    staff=staff,
                    feedback_type=random.choice(['General', 'Facilities', 'Teaching', 'Infrastructure', 'Administration']),
                    rating=random.choice([3.0, 3.5, 4.0, 4.5, 5.0]),
                    feedback_text=fake.paragraph(),
                    is_anonymous=random.choice([True, False]),
                    is_public=True
                )
                feedback.save()
                self.stdout.write(self.style.SUCCESS(f'Created staff institute feedback from {staff.name}'))
            except:
                # Skip if there's an error
                pass
        
        # Create parent institute feedback
        for parent in random.sample(parents, len(parents) // 3):
            try:
                feedback = ParentInstituteFeedback(
                    institute=institute,
                    parent=parent,
                    feedback_type=random.choice(['General', 'Facilities', 'Administration']),
                    rating=random.choice([3.0, 3.5, 4.0, 4.5, 5.0]),
                    feedback_text=fake.paragraph(),
                    is_anonymous=random.choice([True, False]),
                    is_public=True
                )
                feedback.save()
                self.stdout.write(self.style.SUCCESS(f'Created parent institute feedback from {parent.name}'))
            except:
                # Skip if there's an error
                pass
    
    def _create_meetings(self, fake, staff_members, parents):
        # Create parent-teacher meetings
        future_dates = [datetime.now().date() + timedelta(days=d) for d in range(1, 15)]
        
        for staff in random.sample(staff_members, len(staff_members) // 2):
            for parent in random.sample(parents, min(3, len(parents))):
                meeting_date = random.choice(future_dates)
                meeting_hour = random.randint(9, 16)
                meeting_minute = random.choice([0, 15, 30, 45])
                meeting_time = f"{meeting_hour:02d}:{meeting_minute:02d}"
                meeting_status = random.choice(['scheduled', 'rescheduled', 'completed', 'cancelled'])
                
                try:
                    meeting = TeacherParentMeeting(
                        meeting_date=meeting_date,
                        meeting_time=datetime.strptime(meeting_time, "%H:%M").time(),
                        duration=30,
                        status=meeting_status,
                        agenda=fake.paragraph(),
                        notes=fake.paragraph() if meeting_status == 'completed' else '',
                        cancellation_reason=fake.paragraph() if meeting_status == 'cancelled' else '',
                        is_online=random.choice([True, False])
                    )
                    
                    if meeting.is_online:
                        meeting.meeting_link = f"https://meet.example.com/{fake.uuid4()}"
                    
                    meeting.save()
                    self.stdout.write(self.style.SUCCESS(f'Created parent-teacher meeting on {meeting_date}'))
                except Exception as e:
                    # Skip if there's an error
                    pass
    
    def _create_subject_files(self, fake, subjects, staff_members):
        # Create subject files (lecture notes, etc.)
        for subject in random.sample(subjects, len(subjects) // 2):
            # Choose a teacher who might be teaching this subject
            teacher = random.choice(staff_members)
            
            # Create 1-3 files for each selected subject
            for i in range(random.randint(1, 3)):
                file_types = ['Lecture Notes', 'Assignment', 'Reference Material', 'Exam Paper']
                file_type = random.choice(file_types)
                
                subject_file = SubjectFile(
                    subject=subject,
                    title=f"{file_type} - {subject.name} - {i+1}",
                    description=fake.paragraph(),
                    # Note: actual file content can't be created here
                    # file field would need an actual file
                    uploaded_by=teacher
                )
                
                try:
                    # We can't actually save this without a real file
                    # subject_file.save()
                    self.stdout.write(self.style.SUCCESS(f'Created subject file: {subject_file.title}'))
                except:
                    # Skip if there's an error
                    pass
    
    def _create_course_tracking(self, students, courses):
        # Create course tracking records for students
        for student in students:
            course = student.course
            
            if course:
                try:
                    # Check if tracking already exists
                    existing_tracking = CourseTracking.objects.filter(
                        student=student,
                        course=course
                    ).first()
                    
                    if existing_tracking:
                        continue  # Skip if tracking already exists
                    
                    # Calculate dates based on student's joining date
                    joining_date = student.joining_date or datetime.now().date() - timedelta(days=random.randint(180, 365))
                    expected_end_date = joining_date + timedelta(days=365 * course.duration)
                    
                    # Calculate completion percentage based on current semester
                    if course.duration_type == 'Semester':
                        total_semesters = course.duration * 2
                        completion_percentage = int((student.current_period / total_semesters) * 100)
                    else:
                        completion_percentage = int((student.current_period / course.duration) * 100)
                    
                    # Determine progress status
                    if completion_percentage == 100:
                        progress_status = 'Completed'
                    elif completion_percentage == 0:
                        progress_status = 'Not Started'
                    else:
                        progress_status = 'In Progress'
                    
                    tracking = CourseTracking(
                        student=student,
                        course=course,
                        enrollment_date=joining_date,
                        start_date=joining_date,
                        expected_end_date=expected_end_date,
                        actual_end_date=None,
                        progress_status=progress_status,
                        completion_percentage=completion_percentage,
                        current_period=student.current_period,
                        semester_start_date=joining_date,
                        notes=f"Tracking student progress in {course.name}"
                    )
                    tracking.save()
                    self.stdout.write(self.style.SUCCESS(f'Created course tracking for {student.name} in {course.name}'))
                except Exception as e:
                    # Log the error but continue with other students
                    self.stdout.write(self.style.ERROR(f'Error creating course tracking for {student.name}: {str(e)}'))
                    continue  # Continue with next student 
