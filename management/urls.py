from django.urls import path
from BackEnd.management import views

urlpatterns = [
    path('csrf/', views.csrf_token),
    path('register/', views.register_user),
    path('login/', views.login_user),
    
    path('logout/', views.logout_user),
    path('me/', views.current_user),

    path('student/bookings/', views.student_bookings_api),
    path('owner/rooms/', views.owner_rooms_api),

    path('students/', views.manage_student),
    path('students/<int:id>/', views.manage_student),

    path('roles/', views.manage_Role),
    path('roles/<int:id>/', views.manage_Role),

    path('hostels/', views.manage_Hostel),
    path('hostels/<int:id>/', views.manage_Hostel),

    path('administrators/', views.manage_Administrator),
    path('administrators/<int:id>/', views.manage_Administrator),

    path('bookings/', views.manage_booking),
    path('bookings/<int:id>/', views.manage_booking),

    path('hostel_owners/', views.manage_Hostel_owner),
    path('hostel_owners/<int:id>/', views.manage_Hostel_owner),

    path('registers/', views.manage_Registers),
    path('registers/<int:id>/', views.manage_Registers),
]
