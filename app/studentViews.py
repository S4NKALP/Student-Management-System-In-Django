from django.contrib.auth.decorators import login_required

from django.shortcuts import render


@login_required
def student_dashboard(request):
    return render(request, "student/dashboard.html")  # Student-specific page


# @login_required
# @student_required
# def student_view_attendance(request):
#     student = Student.objects.get(admin=request.user.id)
#     course = student.course_id
#     subjects = Subject.objects.filter(course_id=course)
#     student = Student.objects.get(admin=user)
#     student_notifcation = Student.objects.get(admin=request.user.id)
#     notifications = NotificationStudent.objects.filter(
#         student_id=student_notifcation.id
#     )
#     return render(
#         request,
#         "student_template/student_view_attendance.html",
#         {"subjects": subjects, "student": student, "notifications": notifications},
#     )
#
#
# @login_required
# @student_required
# def student_view_attendance_post(request):
#     subject_id = request.POST.get("subject")
#     start_date = request.POST.get("start_date")
#     end_date = request.POST.get("end_date")
#
#     start_data_parse = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
#     end_data_parse = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
#     subject_obj = Subjects.objects.get(id=subject_id)
#     user_object = CustomUser.objects.get(id=request.user.id)
#     stud_obj = Students.objects.get(admin=user_object)
#     user = CustomUser.objects.get(id=request.user.id)
#     student = Students.objects.get(admin=user)
#     student_notifcation = Students.objects.get(admin=request.user.id)
#     notifications = NotificationStudent.objects.filter(
#         student_id=student_notifcation.id
#     )
#
#     attendance = Attendance.objects.filter(
#         attendance_date__range=(start_data_parse, end_data_parse),
#         subject_id=subject_obj,
#     )
#     attendance_reports = AttendanceReport.objects.filter(
#         attendance_id__in=attendance, student_id=stud_obj
#     )
#     return render(
#         request,
#         "student_template/student_attendance_data.html",
#         {
#             "attendance_reports": attendance_reports,
#             "student": student,
#             "notifications": notifications,
#         },
#     )
#
#
# @login_required
# @student_required
# def student_apply_leave(request):
#     student_obj = Student.objects.get(admin=request.user.id)
#     leave_data = LeaveReportStudent.objects.filter(student_id=student_obj)
#     user = CustomUser.objects.get(id=request.user.id)
#     student = Student.objects.get(admin=user)
#     student_notifcation = Student.objects.get(admin=request.user.id)
#     notifications = NotificationStudent.objects.filter(
#         student_id=student_notifcation.id
#     )
#     return render(
#         request,
#         "student/apply_leave.html",
#         {"leave_data": leave_data, "student": student, "notifications": notifications},
#     )
#
#
# @login_required
# @student_required
# def student_apply_leave_save(request):
#     if request.method != "POST":
#         return HttpResponseRedirect(reverse("student_apply_leave"))
#     else:
#         leave_start_date = request.POST.get("leave_start_date")
#         leave_end_date = request.POST.get("leave_end_date")
#         leave_date = request.POST.get("leave_date")
#         leave_msg = request.POST.get("leave_msg")
#
#         student_obj = Student.objects.get(admin=request.user.id)
#         try:
#             leave_report = LeaveReportStudent(
#                 student_id=student_obj,
#                 leave_start_date=leave_start_date,
#                 leave_end_date=leave_end_date,
#                 leave_message=leave_msg,
#                 leave_status=0,
#             )
#             leave_report.save()
#             messages.success(request, "Successfully Applied for Leave")
#             return HttpResponseRedirect(reverse("student_apply_leave"))
#         except:
#             messages.error(request, "Failed To Apply for Leave")
#             return HttpResponseRedirect(reverse("student_apply_leave"))
#
#
# @login_required
# @student_required
# def student_feedback(request):
#     staff_id = Student.objects.get(admin=request.user.id)
#     feedback_data = FeedBackStudent.objects.filter(student_id=staff_id)
#     student = Student.objects.get(admin=user)
#     student_notifcation = Student.objects.get(admin=request.user.id)
#     notifications = NotificationStudent.objects.filter(
#         student_id=student_notifcation.id
#     )
#     return render(
#         request,
#         "student_template/student_feedback.html",
#         {
#             "feedback_data": feedback_data,
#             "student": student,
#             "notifications": notifications,
#         },
#     )
#
#
# @login_required
# @student_required
# def student_feedback_save(request):
#     if request.method != "POST":
#         return HttpResponseRedirect(reverse("student_feedback"))
#     else:
#         feedback_msg = request.POST.get("feedback_msg")
#
#         student_obj = Student.objects.get(admin=request.user.id)
#         try:
#             feedback = FeedBackStudent(
#                 student_id=student_obj, feedback=feedback_msg, feedback_reply=""
#             )
#             feedback.save()
#             messages.success(request, "Feedback submitted for review")
#             return HttpResponseRedirect(reverse("student_feedback"))
#         except:
#             messages.error(request, "Could not Submit")
#             return HttpResponseRedirect(reverse("student_feedback"))
#
#
# @csrf_exempt
# def student_fcmtoken_save(request):
#     token = request.POST.get("token")
#     try:
#         student = Student.objects.get(admin=request.user.id)
#         student.fcm_token = token
#         student.save()
#         return HttpResponse("True")
#     except:
#         return HttpResponse("False")
