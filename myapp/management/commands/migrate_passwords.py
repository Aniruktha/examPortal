from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from myapp.models import Login, TeacherLogin


class Command(BaseCommand):
    help = 'Hash existing plain text passwords in the database'

    def handle(self, *args, **options):
        # Migrate Student passwords
        students = Login.objects.all()
        migrated_count = 0
        for student in students:
            # Check if password is already hashed (starts with pbkdf2_sha256$)
            if not student.password.startswith('pbkdf2_sha256$'):
                student.password = make_password(student.password)
                student.save(update_fields=['password'])
                migrated_count += 1
                self.stdout.write(f'Migrated student: {student.name}')

        self.stdout.write(self.style.SUCCESS(f'\nTotal students migrated: {migrated_count}'))

        # Migrate Teacher passwords
        teachers = TeacherLogin.objects.all()
        teacher_migrated = 0
        for teacher in teachers:
            if not teacher.password.startswith('pbkdf2_sha256$'):
                teacher.password = make_password(teacher.password)
                teacher.save(update_fields=['password'])
                teacher_migrated += 1
                self.stdout.write(f'Migrated teacher: {teacher.name}')

        self.stdout.write(self.style.SUCCESS(f'Total teachers migrated: {teacher_migrated}'))
        self.stdout.write(self.style.SUCCESS('\nPassword migration complete!'))
