
from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length = 30)
    age  = models.IntegerField()
    address = models.CharField(max_length = 200)
    duration = models.IntegerField()
    gender = models.CharField(max_length = 10)

    def __str__(self):
        return self.name

class Hostel_owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length =200)
    address = models.CharField(max_length =200)
    phone = models.CharField(max_length = 20)
    location = models.CharField(max_length =200)

    def __str__(self):
        return self.name       

class Role(models.Model):
    name = models.CharField(max_length = 100)
    description = models.CharField(max_length = 200)

    def __str__(self):
        return self.name


class Administrator(models.Model):
    name = models.CharField(max_length = 200)
    role = models.ForeignKey(Role, on_delete = models.CASCADE, null = True, blank = True)
    phone = models.CharField(max_length =200)


    def __str__(self):
        return self.name


class Hostel(models.Model):
    name = models.CharField(max_length =200)
    #student = models.ForeignKey(Student, on_delete = models.CASCADE, default = True)
    hostel_owner = models.ForeignKey(Hostel_owner, on_delete = models.CASCADE, default = True)
    
    def __str__(self):
        return self.name

class Registers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length = 100)
    Last_name = models.CharField(max_length = 100)
    email_address = models.EmailField(max_length = 100)
    role = models.CharField(max_length = 100)

    def __str__(self):
        return f"{self.first_name} {self.Last_name} ({self.role})"




class Booking(models.Model):
    room = models.ForeignKey(Hostel, on_delete = models.CASCADE)
    name = models.ForeignKey(Student, on_delete = models.CASCADE)
    booking_date = models.DateField(auto_now_add = True)

    def __str__(self):
        return f" The rooom is ready booked by a student"


# Create your models here.
