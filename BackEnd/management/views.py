import logging
import os

from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import DataError, IntegrityError, transaction
from django.db.models import Exists, OuterRef
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Administrator, Booking, Hostel, Hostel_owner, Registers, Role, Student
from .serializer import (
    AdministratorSerializer,
    BookingSerializer,
    HostelSerializer,
    Hostel_ownerSerializer,
    RegistersSerializer,
    RoleSerializer,
    StudentSerializer,
)

logger = logging.getLogger(__name__)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")


def _normalized_role(value):
    role = str(value or "").strip().lower()
    if role in {"hostel owner", "owner"}:
        return "hostel_owner"
    if role in {"student"}:
        return "student"
    return role


def _effective_role_for_user(user):
    register = Registers.objects.filter(user=user).first()
    role = _normalized_role(register.role if register else "")
    if role in {"student", "hostel_owner"}:
        return role
    if Hostel_owner.objects.filter(user=user).exists():
        return "hostel_owner"
    if Student.objects.filter(user=user).exists():
        return "student"
    return ""


def home(request):
    return redirect(f"{FRONTEND_URL}/")


@ensure_csrf_cookie
def react_app(request):
    return redirect(f"{FRONTEND_URL}/")


@api_view(["GET"])
@ensure_csrf_cookie
def csrf_token(request):
    return Response(
        {"message": "CSRF cookie set", "backend": "management", "register_patch": "2026-02-23"},
        status=status.HTTP_200_OK,
    )


def login_page(request):
    return render(request, "login_page.html")


def register_page(request):
    return render(request, "register_page.html")


def about_page(request):
    return render(request, "about_page.html")


@login_required(login_url="/login")
def dashboard_page(request):
    role = _effective_role_for_user(request.user)
    return render(request, "dashboard_page.html", {"role": role, "user": request.user})


@login_required(login_url="/login")
def logout_page(request):
    logout(request)
    return redirect(f"{FRONTEND_URL}/")


@login_required(login_url="/login")
def student_booking_page(request):
    register = Registers.objects.filter(user=request.user, role="student").first()
    if not register:
        return render(request, "message_page.html", {"message": "Only student can access booking page."})

    student = Student.objects.filter(user=request.user).first()
    if not student:
        return render(request, "message_page.html", {"message": "Student profile not found."})

    if request.method == "POST":
        hostel_id = request.POST.get("hostel_id")
        if hostel_id:
            hostel = Hostel.objects.filter(id=hostel_id).first()
            if hostel:
                try:
                    Booking.objects.create(room=hostel, name=student)
                except ValidationError:
                    return render(
                        request,
                        "message_page.html",
                        {"message": "Booking failed: one student can only book one available room."},
                    )

    hostels = Hostel.objects.select_related("hostel_owner").all().order_by("id")
    bookings = Booking.objects.filter(name=student).select_related("room").order_by("-id")
    return render(
        request,
        "student_booking_page.html",
        {"hostels": hostels, "bookings": bookings, "student": student},
    )


@login_required(login_url="/login")
def owner_rooms_page(request):
    register = Registers.objects.filter(user=request.user, role="hostel_owner").first()
    if not register:
        return render(request, "message_page.html", {"message": "Only hostel owner can access room posting page."})

    owner = Hostel_owner.objects.filter(user=request.user).first()
    if not owner:
        return render(request, "message_page.html", {"message": "Hostel owner profile not found."})

    if request.method == "POST":
        room_name = str(request.POST.get("room_name", "")).strip()
        if room_name:
            Hostel.objects.create(name=room_name, hostel_owner=owner)

    rooms = Hostel.objects.filter(hostel_owner=owner).order_by("-id")
    return render(request, "owner_rooms_page.html", {"rooms": rooms, "owner": owner})


def generic_api(model_class, serializer_class):
    @api_view(["GET", "POST", "PUT", "DELETE"])
    def api(request, id=None):
        if request.method == "GET":
            if id:
                try:
                    instance = model_class.objects.get(id=id)
                    serializer = serializer_class(instance)
                    return Response(serializer.data)
                except model_class.DoesNotExist:
                    return Response({"message": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

            instance = model_class.objects.all()
            serializer = serializer_class(instance, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.method == "PUT":
            if not id:
                return Response({"message": "ID is required for update"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                instance = model_class.objects.get(id=id)
                serializer = serializer_class(instance, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except model_class.DoesNotExist:
                return Response({"message": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == "DELETE":
            if not id:
                return Response({"message": "ID is required for delete"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                instance = model_class.objects.get(id=id)
                instance.delete()
                return Response({"message": "Deleted successfully"}, status=status.HTTP_200_OK)
            except model_class.DoesNotExist:
                return Response({"message": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    return api


manage_student = generic_api(Student, StudentSerializer)
manage_Role = generic_api(Role, RoleSerializer)
manage_booking = generic_api(Booking, BookingSerializer)
manage_Hostel = generic_api(Hostel, HostelSerializer)
manage_Hostel_owner = generic_api(Hostel_owner, Hostel_ownerSerializer)
manage_Administrator = generic_api(Administrator, AdministratorSerializer)
manage_Registers = generic_api(Registers, RegistersSerializer)


@api_view(["GET"])
def current_user(request):
    if not request.user.is_authenticated:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    role = _effective_role_for_user(request.user)
    return Response(
        {
            "user_id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "role": role,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def logout_user(request):
    if not request.user.is_authenticated:
        return Response({"message": "Already logged out"}, status=status.HTTP_200_OK)

    logout(request)
    return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
def student_bookings_api(request):
    if not request.user.is_authenticated:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    role = _effective_role_for_user(request.user)
    if role != "student":
        return Response({"message": "Only students can access this endpoint"}, status=status.HTTP_403_FORBIDDEN)

    student = Student.objects.filter(user=request.user).first()
    if not student:
        return Response({"message": "Student profile not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        booked_rooms = Booking.objects.filter(room=OuterRef("pk"))
        # Show only available rooms to students: once booked, room disappears from options.
        bookings = Booking.objects.filter(name=student).select_related("room").order_by("-id")
        if bookings.exists():
            # Student is allowed only one booking at a time.
            hostels = Hostel.objects.none()
        else:
            hostels = (
                Hostel.objects.select_related("hostel_owner")
                .annotate(is_booked=Exists(booked_rooms))
                .filter(is_booked=False)
                .order_by("id")
            )

        hostels_payload = [
            {
                "id": hostel.id,
                "name": hostel.name,
                "owner_name": hostel.hostel_owner.name,
                "owner_id": hostel.hostel_owner.id,
            }
            for hostel in hostels
        ]
        bookings_payload = [
            {
                "id": booking.id,
                "room_id": booking.room.id,
                "room_name": booking.room.name,
                "booking_date": booking.booking_date,
            }
            for booking in bookings
        ]

        return Response(
            {
                "student": {"id": student.id, "name": student.name},
                "hostels": hostels_payload,
                "bookings": bookings_payload,
            },
            status=status.HTTP_200_OK,
        )

    hostel_id = request.data.get("hostel_id")
    if not hostel_id:
        return Response({"message": "hostel_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    if Booking.objects.filter(name=student).exists():
        return Response({"message": "You already have a booking"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        hostel_id = int(hostel_id)
    except (TypeError, ValueError):
        return Response({"message": "hostel_id must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)

    hostel = Hostel.objects.filter(id=hostel_id).first()
    if not hostel:
        return Response({"message": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)

    if Booking.objects.filter(room=hostel, name=student).exists():
        return Response({"message": "You already booked this room"}, status=status.HTTP_400_BAD_REQUEST)

    # One room can only be occupied by one student at a time.
    if Booking.objects.filter(room=hostel).exists():
        return Response({"message": "This room is already booked"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        booking = Booking.objects.create(room=hostel, name=student)
    except ValidationError as exc:
        return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(
        {
            "message": "Booking created successfully",
            "booking": {
                "id": booking.id,
                "room_id": booking.room.id,
                "room_name": booking.room.name,
                "booking_date": booking.booking_date,
            },
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "POST"])
def owner_rooms_api(request):
    if not request.user.is_authenticated:
        return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    role = _effective_role_for_user(request.user)
    if role != "hostel_owner":
        return Response({"message": "Only hostel owners can access this endpoint"}, status=status.HTTP_403_FORBIDDEN)

    owner = Hostel_owner.objects.filter(user=request.user).first()
    if not owner:
        return Response({"message": "Hostel owner profile not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        rooms = Hostel.objects.filter(hostel_owner=owner).order_by("-id")
        bookings = Booking.objects.filter(room__hostel_owner=owner).select_related("name", "room").order_by("-id")
        return Response(
            {
                "owner": {"id": owner.id, "name": owner.name},
                "rooms": [{"id": room.id, "name": room.name} for room in rooms],
                "bookings": [
                    {
                        "id": booking.id,
                        "student_id": booking.name.id,
                        "student_name": booking.name.name,
                        "room_id": booking.room.id,
                        "room_name": booking.room.name,
                        "booking_date": booking.booking_date,
                    }
                    for booking in bookings
                ],
            },
            status=status.HTTP_200_OK,
        )

    room_name = str(request.data.get("room_name", "")).strip()
    if not room_name:
        return Response({"message": "room_name is required"}, status=status.HTTP_400_BAD_REQUEST)
    if len(room_name) > 200:
        return Response({"message": "room_name must be 200 characters or fewer"}, status=status.HTTP_400_BAD_REQUEST)

    room = Hostel.objects.create(name=room_name, hostel_owner=owner)
    return Response(
        {
            "message": "Room posted successfully",
            "room": {"id": room.id, "name": room.name},
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def register_user(request):
    try:
        data = request.data
        if not hasattr(data, "get"):
            return Response(
                {"message": "Validation failed", "errors": {"request": "Invalid payload format"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        first_name = str(data.get("first_name", "")).strip()
        last_name = str(data.get("last_name", "")).strip()
        email = str(data.get("email", "")).strip()
        username = str(data.get("username", "")).strip()
        role = str(data.get("role", "")).strip()
        password = str(data.get("password", ""))
        confirm_password = str(data.get("confirm_password", ""))
        full_name = f"{first_name} {last_name}".strip()

        errors = {}

        if not first_name:
            errors["firstName"] = "First name is required"
        if not last_name:
            errors["lastName"] = "Last name is required"
        if not email:
            errors["email"] = "Email is required"
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors["email"] = "Invalid email address"
        if not username:
            errors["username"] = "Username is required"
        if not role:
            errors["role"] = "Please select a role"
        elif role not in ["student", "hostel_owner"]:
            errors["role"] = "Role must be student or hostel_owner"
        if not password:
            errors["password"] = "Password is required"
        if password != confirm_password:
            errors["confirmPassword"] = "Passwords do not match"
        if User.objects.filter(username=username).exists():
            errors["username"] = "Username already exists"
        if User.objects.filter(email=email).exists():
            errors["email"] = "Email already registered"

        if role == "student":
            if len(full_name) > 30:
                errors["firstName"] = "First and last name are too long for a student profile"
            gender = str(data.get("gender", "Not set")).strip() or "Not set"
            if len(gender) > 10:
                errors["gender"] = "Gender must be 10 characters or fewer"
            try:
                age = int(data.get("age", 18) or 18)
                if age < 1:
                    raise ValueError
            except (TypeError, ValueError):
                errors["age"] = "Age must be a positive number"
            try:
                duration = int(data.get("duration", 1) or 1)
                if duration < 1:
                    raise ValueError
            except (TypeError, ValueError):
                errors["duration"] = "Duration must be a positive number"

        if errors:
            return Response(
                {"message": "Validation failed", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            Registers.objects.create(
                user=user,
                first_name=first_name,
                Last_name=last_name,
                email_address=email,
                role=role,
            )

            if role == "student":
                Student.objects.create(
                    user=user,
                    name=full_name,
                    age=int(data.get("age", 18) or 18),
                    address=str(data.get("address", "Not provided")).strip() or "Not provided",
                    duration=int(data.get("duration", 1) or 1),
                    # Student.gender has max_length=10.
                    gender=str(data.get("gender", "Not set")).strip() or "Not set",
                )
            if role == "hostel_owner":
                Hostel_owner.objects.create(
                    user=user,
                    name=f"{first_name} {last_name}".strip(),
                    address=str(data.get("address", "Not provided")).strip() or "Not provided",
                    phone=str(data.get("phone", "Not provided")).strip() or "Not provided",
                    location=str(data.get("location", "Not provided")).strip() or "Not provided",
                )
    except (ValueError, DataError, IntegrityError):
        return Response(
            {"message": "Invalid registration details"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        logger.exception("Unexpected registration failure")
        return Response(
            {"message": f"Registration failed: {str(exc)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "message": "Registration successful",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def login_user(request):
    data = request.data
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username or not password:
        return Response(
            {
                "message": "Validation failed",
                "errors": {
                    "username": "Username is required" if not username else "",
                    "password": "Password is required" if not password else "",
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)
    if not user:
        return Response(
            {"message": "Invalid username or password"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    login(request, user)
    role = _effective_role_for_user(user)
    return Response(
        {
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": role,
        },
        status=status.HTTP_200_OK,
    )
