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

fake = Faker()

# Nepali-specific data
NEPALI_FIRST_NAMES = [
    'Aarav', 'Aayush', 'Abhishek', 'Aditya', 'Amit', 'Anish', 'Anup', 'Arjun', 'Ashish', 'Bibek',
    'Bikash', 'Bimal', 'Bishal', 'Bishnu', 'Buddha', 'Chandra', 'Dawa', 'Deepak', 'Dinesh', 'Dipesh',
    'Ganesh', 'Gaurav', 'Gopal', 'Hari', 'Hemant', 'Jeevan', 'Karan', 'Krishna', 'Kumar', 'Laxman',
    'Madan', 'Manoj', 'Nabin', 'Narayan', 'Niraj', 'Nishan', 'Prabin', 'Prakash', 'Pramod', 'Prasad',
    'Pratik', 'Pratikshya', 'Rabin', 'Raj', 'Rajesh', 'Rakesh', 'Ram', 'Ramesh', 'Ravi', 'Rohit',
    'Roshan', 'Sagar', 'Sajan', 'Sandeep', 'Sanjay', 'Santosh', 'Saroj', 'Saurav', 'Shankar', 'Shiva',
    'Siddhartha', 'Suman', 'Suresh', 'Sushil', 'Umesh', 'Uttam', 'Vijay', 'Vikash', 'Vishal', 'Yogesh'
]

NEPALI_LAST_NAMES = [
    'Acharya', 'Adhikari', 'Aryal', 'Bajracharya', 'Bhandari', 'Bhattarai', 'Chaudhary', 'Dahal', 'Dangol',
    'Dhakal', 'Gautam', 'Ghimire', 'Gurung', 'Joshi', 'Kafle', 'Karki', 'Khadka', 'Khanal', 'Lama',
    'Limbu', 'Maharjan', 'Malla', 'Neupane', 'Pandey', 'Panta', 'Poudel', 'Rai', 'Rana', 'Regmi',
    'Sharma', 'Shrestha', 'Silwal', 'Singh', 'Tamang', 'Thapa', 'Timalsina', 'Tuladhar', 'Upadhyaya'
]

NEPALI_DESIGNATIONS = [
    'Teacher',
    'Principal',
    'HOD',
    'Admission Officer',
    'Staff'
]

NEPALI_CITIES = [
    'Kathmandu', 'Pokhara', 'Lalitpur', 'Bhaktapur', 'Biratnagar', 'Birgunj', 'Dharan', 'Bharatpur',
    'Butwal', 'Hetauda', 'Dhangadhi', 'Nepalgunj', 'Itahari', 'Damak', 'Siddharthanagar'
]

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
        num_students = max(10, options['students'])  # Ensure minimum of 10 students
        num_staff = max(5, options['staff'])  # Ensure minimum of 5 staff
        num_parents = max(8, options['parents'])  # Ensure minimum of 8 parents
        num_courses = max(3, options['courses'])  # Ensure minimum of 3 courses
        subjects_per_course = max(3, options['subjects'])  # Ensure minimum of 3 subjects per course
        clear_data = options['clear']
        
        # Get or create groups
        staff_group, _ = Group.objects.get_or_create(name='Teacher')
        hod_group, _ = Group.objects.get_or_create(name='HOD')
        admission_officer_group, _ = Group.objects.get_or_create(name='Admission Officer')
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
        staff_members = self._create_staff(fake, num_staff, staff_group, courses)
        
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
    
    def _get_nepali_name(self):
        return f"{random.choice(NEPALI_FIRST_NAMES)} {random.choice(NEPALI_LAST_NAMES)}"

    def _get_nepali_phone(self):
        """Generate a realistic Nepali phone number with proper formatting"""
        # Nepal mobile prefixes (2 digits)
        prefixes = ['98', '97']
        
        # Generate a unique phone number
        while True:
            prefix = random.choice(prefixes)
            # Generate 8 digits after the prefix (no spaces, no formatting)
            digits = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            phone = f"{prefix}{digits}"
            
            # Check if this phone already exists in any user model
            student_exists = Student.objects.filter(phone=phone).exists()
            staff_exists = Staff.objects.filter(phone=phone).exists()
            parent_exists = Parent.objects.filter(phone=phone).exists()
            
            if not (student_exists or staff_exists or parent_exists):
                return phone

    def _get_nepali_address(self, city):
        wards = [f"Ward No. {random.randint(1, 35)}" for _ in range(3)]
        return f"{random.choice(wards)}, {city}, Nepal"

    def _create_institute(self, fake):
        city = random.choice(NEPALI_CITIES)
        institute, created = Institute.objects.get_or_create(
            name=f"{city} Educational Institute",
            defaults={
                'phone': self._get_nepali_phone(),
                'email': fake.company_email(),
                'address': self._get_nepali_address(city),
                'pan_no': f"PAN{random.randint(100000, 999999)}",
                'reg_no': f"REG{random.randint(100000, 999999)}",
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
        subjects = []  # Initialize subjects list
        
        subject_names = {
            'Computer Science Engineering': [
                'Data Structures', 'Algorithms', 'Database Systems', 'Operating Systems',
                'Computer Networks', 'Software Engineering', 'Web Development', 'AI and Machine Learning',
                'Computer Architecture', 'Compiler Design', 'Computer Graphics', 'Cloud Computing'
            ],
            'Electrical Engineering': [
                'Circuit Theory', 'Electrical Machines', 'Power Systems', 'Control Systems',
                'Digital Electronics', 'Microprocessors', 'Power Electronics', 'Electrical Measurements',
                'Renewable Energy', 'Smart Grid', 'High Voltage Engineering', 'Power System Protection'
            ],
            'Mechanical Engineering': [
                'Thermodynamics', 'Fluid Mechanics', 'Manufacturing Processes', 'Machine Design',
                'Heat Transfer', 'Engineering Mechanics', 'Automobile Engineering', 'Materials Science',
                'Robotics', 'CAD/CAM', 'Industrial Engineering', 'Refrigeration and Air Conditioning'
            ],
            'Information Technology': [
                'Programming Fundamentals', 'Data Structures', 'Database Management', 'Web Technologies',
                'Computer Networks', 'Software Engineering', 'Cybersecurity', 'Cloud Computing',
                'Mobile Application Development', 'Big Data Analytics', 'IoT', 'Blockchain Technology'
            ],
            'Data Science': [
                'Statistical Methods', 'Machine Learning', 'Data Mining', 'Big Data Analytics',
                'Data Visualization', 'Deep Learning', 'Natural Language Processing', 'Time Series Analysis',
                'Business Intelligence', 'Predictive Analytics', 'Data Warehousing', 'Data Engineering'
            ]
        }
        
        # Add generic subjects for courses not explicitly defined
        generic_subjects = [
            'Mathematics I', 'Mathematics II', 'Physics', 'Chemistry',
            'Technical Writing', 'Engineering Ethics', 'Project Management', 'Research Methods',
            'Environmental Science', 'Economics', 'Management', 'Communication Skills'
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
                # Calculate number of subjects for this year/semester
                # Ensure at least 2 subjects per year/semester
                num_subjects = max(2, min(subjects_per_course, len(course_subject_names)))
                
                # Select subjects ensuring no duplicates within the same year/semester
                available_subjects = [s for s in course_subject_names if not Subject.objects.filter(
                    course=course,
                    name=s,
                    period_or_year=year_or_sem
                ).exists()]
                
                if len(available_subjects) < num_subjects:
                    # If not enough unique subjects, add some from generic subjects
                    available_subjects.extend([
                        s for s in generic_subjects 
                        if s not in available_subjects and not Subject.objects.filter(
                            course=course,
                            name=s,
                            period_or_year=year_or_sem
                        ).exists()
                    ])
                
                selected_subjects = random.sample(available_subjects, min(num_subjects, len(available_subjects)))
                
                for subject_name in selected_subjects:
                    subject, created = Subject.objects.get_or_create(
                        name=subject_name,
                        course=course,
                        period_or_year=year_or_sem
                    )
                    subjects.append(subject)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created subject: {subject.name} for {course.name} in {year_or_sem}'))
        
        return subjects
    
    def _create_staff(self, fake, num_staff, staff_group, courses):
        staff_members = []
        # Keep track of which courses already have an HOD
        courses_with_hod = set()
        
        for i in range(num_staff):
            try:
                gender = random.choice(['Male', 'Female'])
                name = self._get_nepali_name()
                phone = self._get_nepali_phone()
                city = random.choice(NEPALI_CITIES)
                designation = random.choice(NEPALI_DESIGNATIONS)
                
                staff = Staff(
                    name=name,
                    phone=phone,
                    designation=designation,
                    gender=gender,
                    birth_date=fake.date_of_birth(minimum_age=30, maximum_age=65),
                    email=fake.email(),
                    temporary_address=self._get_nepali_address(city),
                    permanent_address=self._get_nepali_address(city),
                    marital_status=random.choice(['Married', 'Unmarried']),
                    parent_name=self._get_nepali_name(),
                    parent_phone=self._get_nepali_phone(),
                    citizenship_no=f"{random.randint(10000, 99999)}-{random.randint(10000, 99999)}",
                    joining_date=fake.date_between(start_date='-5y', end_date='today')
                )
                
                # First save to get a primary key
                staff.save()
                
                # Set appropriate password based on designation
                password = 'staff123'
                if staff.designation == 'HOD':
                    password = 'hod1234'
                elif staff.designation == 'Admission Officer':
                    password = 'admissionofficer123'
                
                staff.set_password(password)
                
                # Add staff to the appropriate group based on designation
                if staff.designation == 'HOD':
                    hod_group = Group.objects.get(name='HOD')
                    staff.groups.add(hod_group)
                    
                    # Assign a course to HOD that doesn't already have one
                    available_courses = [c for c in courses if c.id not in courses_with_hod]
                    if available_courses:
                        course = random.choice(available_courses)
                        staff.course = course
                        courses_with_hod.add(course.id)
                        staff.save()
                        self.stdout.write(self.style.SUCCESS(f'Assigned HOD {staff.name} to course: {course.name}'))
                    
                elif staff.designation == 'Admission Officer':
                    admission_officer_group = Group.objects.get(name='Admission Officer')
                    staff.groups.add(admission_officer_group)
                else:
                    staff.groups.add(staff_group)
                    
                staff_members.append(staff)
                self.stdout.write(self.style.SUCCESS(f'Created staff: {staff.name} with phone {phone} (password: {password})'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating staff: {str(e)}'))
                continue
        
        return staff_members
    
    def _create_students(self, fake, num_students, courses, batches, student_group):
        students = []
        
        for i in range(num_students):
            try:
                # Generate random personal information
                name = self._get_nepali_name()
                email = fake.email()
                phone = self._get_nepali_phone()
                city = random.choice(NEPALI_CITIES)
                temp_address = self._get_nepali_address(city)
                perm_address = self._get_nepali_address(city)
                birth_date = fake.date_of_birth(minimum_age=18, maximum_age=25)
                
                # Generate random academic information
                course = random.choice(courses)
                batch = random.choice(batches)
                current_period = random.randint(1, course.duration)
                if course.duration_type == 'Semester':
                    current_period = random.randint(1, course.duration * 2)
                
                # Generate random joining date (within last 2 years)
                joining_date = datetime.now().date() - timedelta(days=random.randint(0, 730))
                
                # Create student
                student = Student(
                    name=name,
                    email=email,
                    phone=phone,
                    temporary_address=temp_address,
                    permanent_address=perm_address,
                    birth_date=birth_date,
                    course=course,
                    current_period=current_period,
                    joining_date=joining_date,
                    gender=random.choice(['Male', 'Female', 'Other']),
                    status='Active',
                    is_active=True
                )
                
                # Save the student first to get a primary key
                student.save()
                
                # Set password and save again
                password = 'student123'
                student.set_password(password)
                
                # Add student to batch
                batch.students.add(student)
                
                # Add to student group
                student.groups.add(student_group)
                
                students.append(student)
                self.stdout.write(self.style.SUCCESS(f'Created student {student.name} with phone {phone} (password: {password})'))
            except Exception as e:
                # Log the error but continue with other students
                self.stdout.write(self.style.ERROR(f'Error creating student: {str(e)}'))
                continue  # Continue with next student
        
        return students
    
    def _create_parents(self, fake, num_parents, students, parent_group):
        parents = []
        
        for i in range(num_parents):
            try:
                name = self._get_nepali_name()
                phone = self._get_nepali_phone()
                city = random.choice(NEPALI_CITIES)
                
                parent = Parent(
                    name=name,
                    phone=phone,
                    email=fake.email(),
                    address=self._get_nepali_address(city),
                )
                
                # First save to get a primary key
                parent.save()
                
                # Set password directly using Django's method
                password = 'parent123'
                parent.set_password(password)
                
                # Add parent to group
                parent.groups.add(parent_group)
                
                # Assign students to parent if available
                if students:
                    num_children = min(2, len(students))
                    if num_children > 0:
                        assigned_students = random.sample(students, num_children)
                        for student in assigned_students:
                            parent.students.add(student)
                    
                    self.stdout.write(self.style.SUCCESS(f'Created parent: {parent.name} with phone {phone} (password: {password}) with {num_children} children'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Created parent: {parent.name} with phone {phone} (password: {password}) with no children'))
                
                parents.append(parent)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating parent: {str(e)}'))
                continue
        
        return parents
    
    def _create_routines(self, courses, subjects, staff_members):
        routines = []
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        time_slots = [
            ('09:00', '10:00'),
            ('10:15', '11:15'),
            ('11:30', '12:30'),
            ('13:30', '14:30'),
            ('14:45', '15:45'),
            ('16:00', '17:00')
        ]
        
        # Create a schedule for each course and semester
        for course in courses:
            course_subjects = Subject.objects.filter(course=course)
            
            # Group subjects by period/year
            subjects_by_period = {}
            for subject in course_subjects:
                if subject.period_or_year not in subjects_by_period:
                    subjects_by_period[subject.period_or_year] = []
                subjects_by_period[subject.period_or_year].append(subject)
            
            # Create routine for each period/year
            for period, period_subjects in subjects_by_period.items():
                # Assign teachers to subjects
                teacher_subject_assignments = {}
                available_teachers = staff_members.copy()
                
                for subject in period_subjects:
                    if not available_teachers:
                        available_teachers = staff_members.copy()
                    
                    teacher = random.choice(available_teachers)
                    teacher_subject_assignments[subject] = teacher
                    available_teachers.remove(teacher)
                
                # Create routine for each day
                for day in days_of_week:
                    # Shuffle time slots for variety
                    shuffled_slots = time_slots.copy()
                    random.shuffle(shuffled_slots)
                    
                    # Assign subjects to time slots
                    for subject, teacher in teacher_subject_assignments.items():
                        if not shuffled_slots:
                            break
                            
                        start_time_str, end_time_str = shuffled_slots.pop()
                        start_time = datetime.strptime(start_time_str, "%H:%M").time()
                        end_time = datetime.strptime(end_time_str, "%H:%M").time()
                        
                        # Check for conflicts
                        conflicting_routine = Routine.objects.filter(
                            teacher=teacher,
                            start_time=start_time,
                            end_time=end_time
                        ).first()
                        
                        if not conflicting_routine:
                            routine = Routine(
                                course=course,
                                subject=subject,
                                teacher=teacher,
                                start_time=start_time,
                                end_time=end_time,
                                period_or_year=period,
                                is_active=True
                            )
                            
                            try:
                                routine.save()
                                routines.append(routine)
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'Created routine for {subject.name} with {teacher.name} '
                                        f'on {day} at {start_time_str}-{end_time_str}'
                                    )
                                )
                            except Exception as e:
                                # Skip if there's an error (likely due to unique constraint violation)
                                pass
        
        return routines
    
    def _create_attendance(self, routines, students):
        attendance_records = []
        
        # Create attendance for the past 2 weeks
        for day_offset in range(14, 0, -1):
            date = datetime.now().date() - timedelta(days=day_offset)
            
            # Skip weekends
            if date.weekday() >= 5:  # 5 and 6 are Saturday and Sunday
                continue
            
            for routine in routines:
                # Create attendance for this routine on this date
                attendance = Attendance(
                    date=date,
                    routine=routine,
                    teacher=routine.teacher,
                    teacher_attend=random.choices([True, False], weights=[0.95, 0.05])[0],  # 95% chance of teacher attendance
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
                        # Base attendance probability on student's status
                        if student.status == 'Active':
                            attendance_prob = 0.85  # 85% chance for active students
                        elif student.status == 'Leave':
                            attendance_prob = 0.30  # 30% chance for students on leave
                        else:
                            attendance_prob = 0.10  # 10% chance for completed students
                        
                        # Add some randomness to the attendance pattern
                        attendance_prob += random.uniform(-0.1, 0.1)
                        attendance_prob = max(0, min(1, attendance_prob))  # Ensure between 0 and 1
                        
                        is_present = random.choices([True, False], weights=[attendance_prob, 1-attendance_prob])[0]
                        
                        record = AttendanceRecord(
                            attendance=attendance,
                            student=student,
                            student_attend=is_present
                        )
                        record.save()
                        attendance_records.append(record)
                        
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created attendance for {routine.subject.name} on {date} '
                            f'with {course_students.count()} students'
                        )
                    )
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
            # Each student gives feedback to 2-3 teachers
            num_teachers = random.randint(2, min(3, len(staff_members)))
            selected_teachers = random.sample(staff_members, num_teachers)
            
            for teacher in selected_teachers:
                try:
                    # Generate more realistic ratings (tend to be positive but with some variation)
                    rating = random.choices(
                        [3.5, 4.0, 4.5, 5.0],
                        weights=[0.1, 0.2, 0.3, 0.4]
                    )[0]
                    
                    feedback = StudentFeedback(
                        student=student,
                        teacher=teacher,
                        rating=rating,
                        feedback_text=fake.paragraph()
                    )
                    feedback.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created student feedback from {student.name} for {teacher.name} '
                            f'with rating {rating}'
                        )
                    )
                except:
                    # Skip if there's an error (likely due to unique constraint)
                    pass
        
        # Create parent feedback for teachers
        for parent in random.sample(parents, len(parents) // 2):
            parent_students = parent.students.all()
            if parent_students:
                for student in parent_students:
                    # Each parent gives feedback for 1-2 teachers per student
                    num_teachers = random.randint(1, min(2, len(staff_members)))
                    selected_teachers = random.sample(staff_members, num_teachers)
                    
                    for teacher in selected_teachers:
                        try:
                            # Parent ratings tend to be slightly higher than student ratings
                            rating = random.choices(
                                [4.0, 4.5, 5.0],
                                weights=[0.2, 0.3, 0.5]
                            )[0]
                            
                            feedback = ParentFeedback(
                                parent=parent,
                                teacher=teacher,
                                student=student,
                                rating=rating,
                                feedback_text=fake.paragraph()
                            )
                            feedback.save()
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Created parent feedback from {parent.name} for {teacher.name} '
                                    f'regarding {student.name} with rating {rating}'
                                )
                            )
                        except:
                            # Skip if there's an error
                            pass
        
        # Create institute feedback from students
        for student in random.sample(students, len(students) // 3):
            try:
                # Student institute ratings tend to be slightly lower than teacher ratings
                rating = random.choices(
                    [3.0, 3.5, 4.0, 4.5, 5.0],
                    weights=[0.1, 0.2, 0.3, 0.2, 0.2]
                )[0]
                
                feedback = InstituteFeedback(
                    institute=institute,
                    user=student,
                    feedback_type=random.choice(['General', 'Facilities', 'Teaching', 'Infrastructure', 'Administration']),
                    rating=rating,
                    feedback_text=fake.paragraph(),
                    is_anonymous=random.choice([True, False]),
                    is_public=True
                )
                feedback.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created institute feedback from {student.name} with rating {rating}'
                    )
                )
            except:
                # Skip if there's an error
                pass
        
        # Create staff institute feedback
        for staff in random.sample(staff_members, len(staff_members) // 3):
            try:
                # Staff ratings tend to be more balanced
                rating = random.choices(
                    [3.0, 3.5, 4.0, 4.5, 5.0],
                    weights=[0.15, 0.25, 0.3, 0.2, 0.1]
                )[0]
                
                feedback = StaffInstituteFeedback(
                    institute=institute,
                    staff=staff,
                    feedback_type=random.choice(['General', 'Facilities', 'Teaching', 'Infrastructure', 'Administration']),
                    rating=rating,
                    feedback_text=fake.paragraph(),
                    is_anonymous=random.choice([True, False]),
                    is_public=True
                )
                feedback.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created staff institute feedback from {staff.name} with rating {rating}'
                    )
                )
            except:
                # Skip if there's an error
                pass
        
        # Create parent institute feedback
        for parent in random.sample(parents, len(parents) // 3):
            try:
                # Parent institute ratings tend to be higher
                rating = random.choices(
                    [3.5, 4.0, 4.5, 5.0],
                    weights=[0.1, 0.2, 0.3, 0.4]
                )[0]
                
                feedback = ParentInstituteFeedback(
                    institute=institute,
                    parent=parent,
                    feedback_type=random.choice(['General', 'Facilities', 'Administration']),
                    rating=rating,
                    feedback_text=fake.paragraph(),
                    is_anonymous=random.choice([True, False]),
                    is_public=True
                )
                feedback.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created parent institute feedback from {parent.name} with rating {rating}'
                    )
                )
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
                    
                    # Calculate expected end date based on course duration type
                    if course.duration_type == "Year":
                        years = course.duration
                        duration_days = years * 365
                    else:  # Semester based
                        years = course.duration
                        duration_days = years * 365  # Use full years for total duration
                    
                    expected_end_date = joining_date + timedelta(days=duration_days)
                    
                    # Set period dates based on duration type
                    period_start_date = joining_date
                    if course.duration_type == "Semester":
                        period_end_date = joining_date + timedelta(days=180)  # 6 months
                    else:
                        period_end_date = joining_date + timedelta(days=365)  # 1 year
                    
                    # Create course tracking without nested transaction
                    course_tracking = CourseTracking.objects.create(
                        student=student,
                        course=course,
                        enrollment_date=joining_date,
                        start_date=joining_date,
                        expected_end_date=expected_end_date,
                        current_period=student.current_period,
                        period_start_date=period_start_date,
                        period_end_date=period_end_date,
                        progress_status="In Progress",
                        notes=fake.paragraph() if random.random() < 0.3 else None
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'Created course tracking for student: {student.name} in course: {course.name}'))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating course tracking for student {student.name}: {str(e)}'))
                    continue
