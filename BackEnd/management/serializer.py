from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import *

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'



class Hostel_ownerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel_owner
        fields = '__all__'

class AdministratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrator
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking        
        fields = '__all__'


class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel        
        fields = '__all__'   

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class RegistersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registers
        fields = '__all__'        
