from rest_framework import status
from rest_framework.test import APITestCase

from .models import Hostel, Registers, Student


class StudentApiTests(APITestCase):
    def setUp(self):
        self.list_url = "/api/students/"

    def test_create_student_requires_all_fields(self):
        response = self.client.post(self.list_url, {"name": "OnlyName"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("age", response.data)

    def test_create_student_success(self):
        payload = {
            "name": "John",
            "age": 20,
            "address": "Campus",
            "duration": 12,
            "gender": "Male",
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 1)

    def test_put_without_id_returns_400(self):
        response = self.client.put(self.list_url, {"name": "John"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "ID is required for update")

    def test_delete_without_id_returns_400(self):
        response = self.client.delete(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "ID is required for delete")


class RegistrationApiTests(APITestCase):
    def setUp(self):
        self.register_url = "/api/register/"

    def test_register_student_without_gender_works(self):
        payload = {
            "first_name": "Demo",
            "last_name": "Student",
            "email": "demo_student_api@example.com",
            "username": "demo_student_api",
            "role": "student",
            "password": "pass12345",
            "confirm_password": "pass12345",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Student.objects.filter(user__username="demo_student_api").exists())
        self.assertTrue(Registers.objects.filter(user__username="demo_student_api").exists())

    def test_register_with_invalid_duration_returns_400(self):
        payload = {
            "first_name": "Demo",
            "last_name": "Student",
            "email": "demo_student_invalid_duration@example.com",
            "username": "demo_student_invalid_duration",
            "role": "student",
            "password": "pass12345",
            "confirm_password": "pass12345",
            "duration": "not-a-number",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Validation failed")
        self.assertIn("duration", response.data.get("errors", {}))

    def test_login_success_after_register(self):
        payload = {
            "first_name": "Login",
            "last_name": "User",
            "email": "login_user@example.com",
            "username": "login_user",
            "role": "student",
            "password": "pass12345",
            "confirm_password": "pass12345",
        }
        register_response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        login_response = self.client.post(
            "/api/login/",
            {"username": "login_user", "password": "pass12345"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(login_response.data["username"], "login_user")
        self.assertEqual(login_response.data["role"], "student")

    def test_login_wrong_password_returns_401(self):
        payload = {
            "first_name": "Login",
            "last_name": "Fail",
            "email": "login_fail@example.com",
            "username": "login_fail",
            "role": "student",
            "password": "pass12345",
            "confirm_password": "pass12345",
        }
        register_response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        login_response = self.client.post(
            "/api/login/",
            {"username": "login_fail", "password": "wrong-pass"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(login_response.data["message"], "Invalid username or password")


class BookingAndOwnerFlowTests(APITestCase):
    def setUp(self):
        self.register_url = "/api/register/"
        self.login_url = "/api/login/"
        self.logout_url = "/api/logout/"
        self.owner_rooms_url = "/api/owner/rooms/"
        self.student_bookings_url = "/api/student/bookings/"

        self.owner_payload = {
            "first_name": "Owner",
            "last_name": "One",
            "email": "owner_one@example.com",
            "username": "owner_one",
            "role": "hostel_owner",
            "password": "pass12345",
            "confirm_password": "pass12345",
            "phone": "0700000000",
            "location": "Town",
        }
        self.student_payload = {
            "first_name": "Student",
            "last_name": "One",
            "email": "student_one@example.com",
            "username": "student_one",
            "role": "student",
            "password": "pass12345",
            "confirm_password": "pass12345",
            "age": 21,
            "duration": 6,
            "gender": "Male",
            "address": "Campus",
        }

    def _register(self, payload):
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def _login(self, username, password="pass12345"):
        response = self.client.post(
            self.login_url,
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data

    def _logout(self):
        self.client.post(self.logout_url, {}, format="json")

    def test_owner_can_post_room_and_student_can_book(self):
        self._register(self.owner_payload)
        self._register(self.student_payload)

        self._login("owner_one")
        post_room = self.client.post(self.owner_rooms_url, {"room_name": "A-101"}, format="json")
        self.assertEqual(post_room.status_code, status.HTTP_201_CREATED)
        room_id = post_room.data["room"]["id"]
        self._logout()

        self._login("student_one")
        get_rooms = self.client.get(self.student_bookings_url, format="json")
        self.assertEqual(get_rooms.status_code, status.HTTP_200_OK)
        self.assertTrue(any(room["id"] == room_id for room in get_rooms.data["hostels"]))

        book_room = self.client.post(self.student_bookings_url, {"hostel_id": room_id}, format="json")
        self.assertEqual(book_room.status_code, status.HTTP_201_CREATED)

        duplicate = self.client.post(self.student_bookings_url, {"hostel_id": room_id}, format="json")
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(duplicate.data["message"], "You already have a booking")

    def test_role_restrictions_on_endpoints(self):
        self._register(self.owner_payload)
        self._register(self.student_payload)

        self._login("student_one")
        student_post_room = self.client.post(self.owner_rooms_url, {"room_name": "B-201"}, format="json")
        self.assertEqual(student_post_room.status_code, status.HTTP_403_FORBIDDEN)
        self._logout()

        self._login("owner_one")
        owner_booking_access = self.client.get(self.student_bookings_url, format="json")
        self.assertEqual(owner_booking_access.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_room_name_too_long_returns_400(self):
        self._register(self.owner_payload)
        self._login("owner_one")

        long_name = "R" * 201
        response = self.client.post(self.owner_rooms_url, {"room_name": long_name}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "room_name must be 200 characters or fewer")
        self.assertEqual(Hostel.objects.count(), 0)

    def test_student_booking_with_invalid_hostel_id_returns_400(self):
        self._register(self.student_payload)
        self._login("student_one")

        response = self.client.post(self.student_bookings_url, {"hostel_id": "abc"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "hostel_id must be a valid number")

    def test_two_students_cannot_book_same_room(self):
        self._register(self.owner_payload)
        self._register(self.student_payload)

        second_student = {
            "first_name": "Student",
            "last_name": "Two",
            "email": "student_two@example.com",
            "username": "student_two",
            "role": "student",
            "password": "pass12345",
            "confirm_password": "pass12345",
            "age": 22,
            "duration": 4,
            "gender": "Male",
            "address": "Campus 2",
        }
        self._register(second_student)

        self._login("owner_one")
        post_room = self.client.post(self.owner_rooms_url, {"room_name": "C-301"}, format="json")
        self.assertEqual(post_room.status_code, status.HTTP_201_CREATED)
        room_id = post_room.data["room"]["id"]
        self._logout()

        self._login("student_one")
        first_booking = self.client.post(self.student_bookings_url, {"hostel_id": room_id}, format="json")
        self.assertEqual(first_booking.status_code, status.HTTP_201_CREATED)
        self._logout()

        self._login("student_two")
        available_rooms = self.client.get(self.student_bookings_url, format="json")
        self.assertEqual(available_rooms.status_code, status.HTTP_200_OK)
        self.assertFalse(any(room["id"] == room_id for room in available_rooms.data["hostels"]))

        second_booking = self.client.post(self.student_bookings_url, {"hostel_id": room_id}, format="json")
        self.assertEqual(second_booking.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(second_booking.data["message"], "This room is already booked")

    def test_student_cannot_book_second_room(self):
        self._register(self.owner_payload)
        self._register(self.student_payload)

        self._login("owner_one")
        room1 = self.client.post(self.owner_rooms_url, {"room_name": "D-401"}, format="json")
        self.assertEqual(room1.status_code, status.HTTP_201_CREATED)
        room2 = self.client.post(self.owner_rooms_url, {"room_name": "D-402"}, format="json")
        self.assertEqual(room2.status_code, status.HTTP_201_CREATED)
        room1_id = room1.data["room"]["id"]
        room2_id = room2.data["room"]["id"]
        self._logout()

        self._login("student_one")
        first_booking = self.client.post(self.student_bookings_url, {"hostel_id": room1_id}, format="json")
        self.assertEqual(first_booking.status_code, status.HTTP_201_CREATED)

        second_booking = self.client.post(self.student_bookings_url, {"hostel_id": room2_id}, format="json")
        self.assertEqual(second_booking.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(second_booking.data["message"], "You already have a booking")
