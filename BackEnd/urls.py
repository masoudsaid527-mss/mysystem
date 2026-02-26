import os

from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from BackEnd.management import views

# FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")

urlpatterns = [
    path('admin/', admin.site.urls),

    # path('', RedirectView.as_view(url=f'{FRONTEND_URL}/', permanent=False)),
    # path('app', RedirectView.as_view(url=f'{FRONTEND_URL}/', permanent=False)),
    # re_path(r'^app/.*$', RedirectView.as_view(url=f'{FRONTEND_URL}/', permanent=False)),

    # path('home', RedirectView.as_view(url=f'{FRONTEND_URL}/', permanent=False)),
    # path('login', RedirectView.as_view(url=f'{FRONTEND_URL}/', permanent=False)),
    # path('register', RedirectView.as_view(url=f'{FRONTEND_URL}/', permanent=False)),
    # path('about', RedirectView.as_view(url=f'{FRONTEND_URL}/', permanent=False)),

    # path('dashboard', views.dashboard_page),
    # path('logout', views.logout_page),
    # path('student/book', views.student_booking_page),
    # path('owner/rooms', views.owner_rooms_page),

    path('api/', include('BackEnd.management.urls')),
]
