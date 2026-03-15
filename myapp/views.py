from django.shortcuts import render,HttpResponse, redirect, get_object_or_404
from .models import Login,Testfiles, Scores, Login, Courses,ClassCourses, StudentTestRecord, TeacherLogin
from .forms import FileUploadForm, Loginform, StudentRegistrationForm, TeacherRegistrationForm, StudentLoginForm, TeacherLoginForm
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.utils.timezone import now, make_aware
import pytz

IST = pytz.timezone("Asia/Kolkata")  # Define IST timezone globally

def about_us(request):
    return render(request, 'aboutUs.html')

# Create your views here.
def get_courses(username):
    course_map={
        'pw':"Software Systems",
        'pc':"Cyber Security",
        'pt':"Theoritical Computer Science",
        'pd':"Data Science"
    }
    course_key=username[2:4]
    return course_map.get(course_key, "Unknown Course")


def login_details(request):
    """Original login view - redirects to role-specific login"""
    return redirect('student_login')


def student_login(request):
    """Student Login View - Separate from Teacher Login"""
    if request.method == "POST":
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            # Password already validated by form's clean() method using check_password
            user = Login.objects.filter(name=username).first()

            if user:
                request.session['username'] = user.name  
                course = get_courses(user.name)
                request.session['course'] = course  
                return redirect("home")
            else:
                return render(request, "student_login.html", {"form": form, "error": "Invalid credentials"})
    else:
        form = StudentLoginForm()

    return render(request, "student_login.html", {"form": form})


def teacher_login(request):
    """Teacher Login View - Separate from Student Login"""
    if request.method == "POST":
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            # Password already validated by form's clean() method using check_password
            user = TeacherLogin.objects.filter(name=username).first()

            if user:
                request.session['username'] = user.name  
                request.session['course'] = 'Teacher'  
                return redirect("upload_file")
            else:
                return render(request, "teacher_login.html", {"form": form, "error": "Invalid credentials"})
    else:
        form = TeacherLoginForm()

    return render(request, "teacher_login.html", {"form": form})


def student_register(request):
    """Student Registration View - Sign up for new students"""
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            # Extract course from username (format: 23pw001)
            course_key = username[2:4]
            course_map = {
                'pw': "Software Systems",
                'pc': "Cyber Security",
                'pt': "Theoritical Computer Science",
                'pd': "Data Science"
            }
            course = course_map.get(course_key, "Unknown Course")

            # Create new student with hashed password
            student = Login.objects.create(
                name=username,
                password=make_password(password),  # Hash the password!
                mail=email,
                course=course
            )
            student.save()

            return render(request, "student_register.html", {
                "form": StudentRegistrationForm(),
                "success": "Registration successful! Please login."
            })
    else:
        form = StudentRegistrationForm()

    return render(request, "student_register.html", {"form": form})


def teacher_register(request):
    """Teacher Registration View - Sign up for new teachers"""
    if request.method == "POST":
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Create new teacher with hashed password
            teacher = TeacherLogin.objects.create(
                name=username,
                password=make_password(password)  # Hash the password!
            )
            teacher.save()

            return render(request, "teacher_register.html", {
                "form": TeacherRegistrationForm(),
                "success": "Registration successful! Please login."
            })
    else:
        form = TeacherRegistrationForm()

    return render(request, "teacher_register.html", {"form": form})


def profile_view(request):
    print("Session Data:", request.session.items()) 
    print("Authenticated:", request.user.is_authenticated)
    print("User:", request.user)  # Check the logged-in user

    username = request.session.get("username")  # Retrieve username from session

    if username:
        try:
            user = Login.objects.get(name=username)  # Fetch user from the Login table
            course_name = request.session.get("course")  # Get course from session

            if not course_name or course_name == "Unknown Course":  # If not stored, fetch from DB
                course_code = username[2:4]  # Extract course code
                course = Courses.objects.filter(courseID=course_code).first()
                course_name = course.courseName if course else "Unknown Course"
                request.session["course"] = course_name  # Store it for future use
            
        except Login.DoesNotExist:
            user, course_name = None, "Unknown Course"  # Handle case where user is not found

    else:
        user, course_name = None, "Unknown Course"  # No username in session, user not logged in

    return render(request, "profile.html", {"user": user, "course_name": course_name})




def upload_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)  # Create but don't save yet

            # Convert start & stop times to timezone-aware datetimes
            from datetime import timezone  # Add this at the top

            obj.startTime = form.cleaned_data["startTime"].astimezone(timezone.utc)
            obj.endTime = form.cleaned_data["endTime"].astimezone(timezone.utc)
            
            obj.save()  # Now save with timezone-aware timestamps
            print("file saved successfully")
            return render(request, 'fileupload.html', {'form': FileUploadForm(), 'success': True})

    else:
        form = FileUploadForm()

    return render(request, 'fileupload.html', {'form': form})



from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from .models import Testfiles, Login, StudentTestRecord, Scores

def Taketest(request, fileName):
    test = get_object_or_404(Testfiles, Qfiles__icontains=fileName)
    username = request.session.get('username')
    if not username:
        return redirect('login')  # Redirect to login if session is invalid
    student = get_object_or_404(Login, name=username)

    # ✅ Check if the student has already taken the test
    test_record, created = StudentTestRecord.objects.get_or_create(student=student, test=test)
    if test_record.status:
        return redirect('review_test', test_id=test.id)

    # ✅ Parse questions FIRST (needed for both GET and POST)
    queFilePath = test.Qfiles.path
    ansFilePath = test.Afiles.path

    # ✅ Read question file
    try:
        with open(queFilePath, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading question file: {e}")
        return render(request, 'test.html', {'error': 'Could not load questions'})

    # ✅ Read answer file
    try:
        with open(ansFilePath, 'r') as f:
            correct_answers = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading answer file: {e}")
        return render(request, 'test.html', {'error': 'Could not load answers'})

    # ✅ Parse questions and options
    questions = []
    i = 0
    while i < len(lines):
        if i + 4 >= len(lines):
            break
        question_text = lines[i]
        options = lines[i+1:i+5]
        i += 5

        if len(options) == 4:
            questions.append({'question': question_text, 'options': options})

    # ✅ Handle form submission FIRST (before checking time)
    if request.method == "POST":
        import logging
        logger = logging.getLogger(__name__)
        logger.error("POST DATA: " + str(request.POST))
        print("=" * 50)
        print("POST DATA:", dict(request.POST))
        print("=" * 50)
        
        user_answers = [request.POST.get(f"q{i}", "Not Answered") for i in range(len(questions))]
        
        print("User answers:", user_answers)
        print("Questions count:", len(questions))
        
        correct = [idx for idx in range(len(user_answers)) if idx < len(correct_answers) and user_answers[idx] == correct_answers[idx]]
        incorrect = [idx for idx in range(len(user_answers)) if idx not in correct]

        # ✅ Save results in StudentTestRecord
        test_record.user_answers = user_answers
        test_record.correct_answers = [correct_answers[i] for i in correct]
        test_record.incorrect_answers = incorrect
        test_record.score = len(correct)
        test_record.status = True
        test_record.save()

        # ✅ Save score in Scores model
        Scores.objects.create(
            student=student,
            test=test,
            courseCode=student.name[2:4],
            marks=len(correct)
        )

        return redirect('review_test', test_id=test.id)

    # ✅ Check if the test time window is valid (only for GET requests)
    current_time = now()
    if not (test.startTime <= current_time <= test.endTime):
        # Time exceeded - redirect to review
        return redirect('review_test', test_id=test.id)

    # Convert endTime to a JavaScript-friendly format (ISO string with timezone)
    test_endtime_iso = test.endTime.isoformat()
    return render(request, 'test.html', {
        'test': test, 
        'questions': questions, 
        'fileName': test.Qfiles.name.split('/')[-1],
        'test_endtime_iso': test_endtime_iso
    })





def home(request):
    username = request.session.get('username')  # ✅ Retrieve username from session
    
    if not username:
        return redirect('/')
    
    classid=username[:4]

    courses=Courses.objects.filter(courseID__in=ClassCourses.objects.filter(classid=classid).values('courseID'))
    print("Courses found: ",courses)
    
    context = {'name': username, 'courses':courses}
    return render(request, 'home.html', context)



def course_test(request, course_id):
    course = get_object_or_404(Courses, courseID=course_id)  # Ensure course exists
    student = get_object_or_404(Login, name=request.session.get('username'))
    tests = Testfiles.objects.filter(courseCode=course_id)

    ist = pytz.timezone("Asia/Kolkata")
    local_now = timezone.now().astimezone(ist)

    for test in tests:
        test.startTime = test.startTime.astimezone(ist)  # Convert to IST
        test.endTime = test.endTime.astimezone(ist)  # Convert to IST
        test.Qfiles.name = test.Qfiles.name.replace("uploads/", "")
        
        test.is_test_active = test.is_active

         # Check if the student has already taken the test
        test_record = StudentTestRecord.objects.filter(student=student, test=test).first()
        test.taken = bool(test_record)  # True if test is already taken

        score_record = Scores.objects.filter(student=student, test=test).first()
        test.score = score_record.marks if score_record else None  # Store score in test object

        # Determine if the test is active
        print(f"Test: {test.name}, Start: {test.startTime}, End: {test.endTime}, Now: {local_now}")
    return render(request, 'CoursesTest.html', {'tests': tests, 'course': course})

from django.shortcuts import get_object_or_404, render

import logging

logger = logging.getLogger(__name__)

def review_test(request, test_id):
    test = get_object_or_404(Testfiles, id=test_id)
    student = get_object_or_404(Login, name=request.session.get('username'))
    test_record = get_object_or_404(StudentTestRecord, student=student, test=test)

    ansFilePath = test.Afiles.path
    queFilePath = test.Qfiles.path

    # ✅ Load correct answers
    with open(ansFilePath, 'r') as f:
        correct_answers = [line.strip() for line in f.readlines() if line.strip()]

    # ✅ Load questions
    questions = []
    with open(queFilePath, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    i = 0
    while i < len(lines):
        question_text = lines[i]
        options = lines[i+1:i+5]  # Next 4 lines are options
        i += 5  # Move to the next question

        if options:
            questions.append({'question': question_text, 'options': options})

    # ✅ Handle missing fields gracefully
    correct_indices = getattr(test_record, 'correct_answers', [])
    incorrect_indices = getattr(test_record, 'incorrect_answers', [])

    user_answers = getattr(test_record, 'user_answers', [""] * len(questions))
    # ✅ Construct the review structure
    questions_review = []
    for index, question in enumerate(questions):
        correct_ans = correct_answers[index] if index < len(correct_answers) else "N/A"
        selected_ans = user_answers[index] if index < len(user_answers) else "Not Answered"
        is_correct = index in correct_indices
        is_incorrect = index in incorrect_indices

        questions_review.append({
            'question': question['question'],
            'options': question['options'],
            'correct_answer': correct_ans,
            'selected_answer': selected_ans,
            'is_correct': is_correct,
            'is_incorrect': is_incorrect
        })

    logger.debug(f"Review Questions: {questions_review}")  # ✅ Debugging

    print(f"Retrieved user_answers in review page: {user_answers}")

    return render(request, 'review_test.html', {
        'test': test,
        'questions_review': questions_review,
        'user_answers': user_answers,
        'correct_answers': correct_answers
    })



def test_list(request):
    student = request.user  # Assuming you are fetching tests for the logged-in student
    tests = Testfiles.objects.filter(course=student.course)  # Adjust filtering as needed

    # Set active status based on time
    ist = pytz.timezone("Asia/Kolkata")  # Change to your timezone
    local_now = timezone.now().astimezone(ist)

    for test in tests:
        test.startTime = test.startTime.astimezone(ist)
        test.endTime = test.endTime.astimezone(ist)
        test.is_active = test.startTime <= local_now <= test.endTime

        print(f"Test: {test.name}, Start: {test.startTime}, End: {test.endTime}, Now: {local_now}, Active: {test.is_active}")

    return render(request, "tests.html", {"tests": tests, "student": student})


from django.http import JsonResponse
from myapp.models import Testfiles  # Import your model
from datetime import datetime

def get_tests(request):
    tests = Testfiles.objects.all()
    work_schedule = {}

    for test in tests:
        test_date = test.startTime.strftime("%Y-%m-%d")  # Extract only the date part
        if test_date not in work_schedule:
            work_schedule[test_date] = []
        work_schedule[test_date].append(test.name)  # Assuming `name` column stores test name

    return JsonResponse(work_schedule)

from django.shortcuts import redirect
from django.contrib.auth import logout

def logout_view(request):
    logout(request)  # Logs out the user
    return redirect('/')  # Redirect to login page (Change 'login' to your actual login URL name)