from django.urls import path
from . import views
from .views import upload_file, Taketest, home,course_test, review_test, about_us, profile_view, get_tests, logout_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.login_details, name="Login"),
    path('home/', home, name='home'),
    path("aboutus/", views.about_us, name="aboutus"),
    path("profile/", profile_view, name="profile"),
    path('upload/',upload_file,name='upload_file'),
    path('api/tests/', get_tests, name='get_tests'),
    path('test/<str:fileName>/',Taketest, name='Taketest'),
    path('courses/<str:course_id>/', course_test, name='courses_test'),
    path('review/<int:test_id>/', review_test, name='review_test'),
    path("logout/", logout_view, name="logout"),


]

if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])