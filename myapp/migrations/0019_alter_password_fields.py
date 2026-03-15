from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0018_remove_login_stuname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='login',
            name='password',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='teacherlogin',
            name='password',
            field=models.CharField(max_length=128),
        ),
    ]
