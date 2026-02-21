from rest_framework import status
from rest_framework.test import APITestCase

from .models import Registers, Student


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
        self.assertEqual(response.data["message"], "Invalid registration details")
