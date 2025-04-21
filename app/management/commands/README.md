# Fake Data Generator for SMS

This directory contains a Django management command to generate fake data for testing the School Management System (SMS).

## Prerequisites

Before using this script, make sure you have installed the required packages:

```bash
pip install faker
```

## Usage

Run the command using Django's `manage.py`:

```bash
python manage.py generate_fake_data
```

### Options

The script accepts the following optional parameters:

- `--students`: Number of students to create (default: 50)
- `--staff`: Number of staff members to create (default: 20)
- `--parents`: Number of parents to create (default: 40)
- `--courses`: Number of courses to create (default: 5)
- `--subjects`: Number of subjects per course (default: 4)
- `--clear`: Clear existing data before generating new data (flag)

### Examples

Generate data with default parameters:
```bash
python manage.py generate_fake_data
```

Generate a smaller dataset:
```bash
python manage.py generate_fake_data --students 20 --staff 10 --parents 15
```

Clear existing data and generate new data:
```bash
python manage.py generate_fake_data --clear
```

## Generated Data

The script generates the following types of data:

1. Institute information
2. Batches (last 4 years)
3. Courses with customized names and durations
4. Subjects for each course
5. Staff members with profiles and credentials
6. Students with profiles and course assignments
7. Parents linked to students
8. Class routines and schedules
9. Attendance records for past two weeks
10. Notices/announcements
11. Leave requests for students and staff
12. Feedback (student, parent, institute)
13. Parent-teacher meetings
14. Course tracking records

## Login Credentials

The generated users have the following default passwords:

- Students: `student123`
- Regular Staff/Teachers: `staff123`
- Department Heads (HOD): `hod1234`
- Admission Officers: `admissionofficer123`
- Parents: `parent123`

## User Groups

The following user groups are created automatically:

- Student
- Teacher 
- HOD (Department Heads)
- Admission Officer
- Parent

Each group has appropriate permissions assigned based on their role in the system.

## Phone Numbers

All users are assigned unique 10-digit Nepali phone numbers (e.g., 98xxxxxxxx, 97xxxxxxxx). These phone numbers are used as the username for authentication.

## Note

The script doesn't generate actual file content for subject files due to the limitation of creating binary content programmatically. This portion is commented out in the code.

## Troubleshooting

If you encounter issues with transactions or database errors, try running the command with the `--clear` flag to start with a clean database before generating new data. 