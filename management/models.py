from django.db import models

class Student(models.Model):
    name = models.CharField(max_length = 30)
    age  = models.IntegerField()
    address = models.CharField(max_length = 200)
    duration = models.IntegerField()
    gender = models.CharField(max_length = 10)

    def __str__(self):
        return self.name

class Hostel_owner(models.Model):
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
    student = models.ForeignKey(Student, on_delete = models.CASCADE, default = True)
    hostel_owner = models.ForeignKey(Hostel_owner, on_delete = models.CASCADE, default = True)
    def __str__(self):
        return self.name


class Booking(models.Model):
    room = models.IntegerField(default = True)
    name = models.ForeignKey(Student, on_delete = models.CASCADE)
    booking_date = models.DateField(auto_now_add = True)

    def __str__(self):
        return f" The rooom is ready booked by a student"


# Create your models here.
