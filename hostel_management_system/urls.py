from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from management import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(url='/app/', permanent=False)),
    path('app', views.react_app),
    re_path(r'^app/.*$', views.react_app),

    path('home', RedirectView.as_view(url='/app/', permanent=False)),
    path('login', RedirectView.as_view(url='/app/login', permanent=False)),
    path('register', RedirectView.as_view(url='/app/register', permanent=False)),
    path('about', RedirectView.as_view(url='/app/about', permanent=False)),

    path('dashboard', views.dashboard_page),
    path('logout', views.logout_page),
    path('student/book', views.student_booking_page),
    path('owner/rooms', views.owner_rooms_page),

    path('api/', include('management.urls')),
]
