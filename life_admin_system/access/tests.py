from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AdministratorModelTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            email="user@test.com",
            password="pass1234"
        )
        self.assertEqual(user.email, "user@test.com")
        self.assertTrue(user.check_password("pass1234"))
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@test.com",
            password="adminpass"
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

