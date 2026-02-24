from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from management import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(url='http://localhost:5175/', permanent=False)),
    path('app', RedirectView.as_view(url='http://localhost:5175/', permanent=False)),
    re_path(r'^app/.*$', RedirectView.as_view(url='http://localhost:5175/', permanent=False)),

    path('home', RedirectView.as_view(url='http://localhost:5175/', permanent=False)),
    path('login', RedirectView.as_view(url='http://localhost:5175/', permanent=False)),
    path('register', RedirectView.as_view(url='http://localhost:5175/', permanent=False)),
    path('about', RedirectView.as_view(url='http://localhost:5175/', permanent=False)),

    path('dashboard', views.dashboard_page),
    path('logout', views.logout_page),
    path('student/book', views.student_booking_page),
    path('owner/rooms', views.owner_rooms_page),

    path('api/', include('management.urls')),
]
