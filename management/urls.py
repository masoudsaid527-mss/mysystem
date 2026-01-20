from django.urls import path
from management import views


urlpatterns = [
    path('students/', views.manage_student),
    path('students/<int:id>', views.manage_student),
    path('roles/', views.manage_Role),
    path('roles/<int:id>', views.manage_Role),
]