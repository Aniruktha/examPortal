from django.db import models
from django.utils import timezone
from django.utils.timezone import now
import pytz
from django.utils.timezone import make_aware, localtime

IST = pytz.timezone("Asia/Kolkata")

# Create your models here.
class Login(models.Model):
    name=models.CharField(max_length=50, null=False)
    password=models.CharField(max_length=128, null=False)  # Increased for hashed passwords
    mail=models.EmailField(default=None)
    course=models.CharField(max_length=50, null=False, blank=False, default=None)

    def save(self, *args, **kwargs):
        if not self.course:  # Set course only if not already set
            self.course = self.get_course_from_name()
        super().save(*args, **kwargs)

    def get_course_from_name(self):
        course_map = {
            'pw': "Software Systems",
            'pc': "Cyber Security",
            'pt': "Theoretical Computer Science",
            'pd': "Data Science"
        }
        course_key = self.name[2:4]  # Extracting course key from name
        return course_map.get(course_key, "Unknown Course")

    class Meta:
        db_table="login"
    def __str__(self):
        return self.name

class TeacherLogin(models.Model):
    name=models.CharField(max_length=50, null=False)
    password=models.CharField(max_length=128, null=False)  # Increased for hashed passwords

    class Meta:
        db_table="teacherLogin"
    def __str__(self):
        return self.name
    
class Testfiles(models.Model):
    name=models.CharField(max_length=50, null=False, unique=True)
    Qfiles=models.FileField(upload_to='uploads/')
    Afiles=models.FileField(upload_to='uploads/')
    startTime=models.DateTimeField()
    endTime=models.DateTimeField()
    courseCode=models.CharField(max_length=6,null=False)
    uploaded_at=models.DateTimeField(auto_now_add=True)

    @property
    def is_active(self):
        """Check if the test is active (IST time)."""
        local_now = localtime(timezone.now(), IST)
        return self.startTime.astimezone(IST) <= local_now <= self.endTime.astimezone(IST)


class Scores(models.Model):
    student = models.ForeignKey(Login, on_delete=models.CASCADE)  # Student roll number
    test = models.ForeignKey(Testfiles, on_delete=models.CASCADE, db_column='test_id')  # Test ID
    courseCode = models.CharField(max_length=4)  # Course Code
    marks = models.IntegerField()  # Marks obtained

    def __str__(self):
        return f"{self.student.name} - {self.test.name} - {self.marks}"

class Courses(models.Model):
    courseID = models.CharField(max_length=10, primary_key=True)
    courseName = models.CharField(max_length=50)

class ClassCourses(models.Model):
    classid = models.CharField(max_length=10)  # e.g., "23pw"
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('classid', 'courseID')  # Prevent duplicate entries


class StudentTestRecord(models.Model):
    id = models.AutoField(primary_key=True) 
    student = models.ForeignKey(Login, on_delete=models.CASCADE)  # Links to Login model
    test = models.ForeignKey(Testfiles, on_delete=models.CASCADE)  # Links to Testfiles model
    user_answers = models.JSONField(default=list) 
    score = models.IntegerField(null=True, blank=True)  # Match data type with Scores.marks
    status = models.BooleanField(default=False)  # Indicates if the student passed
    correct_answers = models.JSONField(default=list)  # Stores correct answer indices
    incorrect_answers = models.JSONField(default=list)  # Stores incorrect answer indices

    def __str__(self):
        return f"{self.student.name} - {self.test.name} - Score: {self.score}"
