import pytest
from django.urls import reverse

from profiles.models import CustomUser


class UserFactory:
    """Factory class to create users for tests"""

    @staticmethod
    def create(email, password, is_superuser=False):
        user = CustomUser.objects.create_user(email=email, password=password)

        if is_superuser:
            user.is_staff = True
            user.is_superuser = True
            user.save()

        return user


@pytest.fixture
def user_factory(db):
    """Fixture that returns the UserFactory"""
    return UserFactory()


class TestUserModel:
    """Class-based tests for User model"""

    def test_user_creation(self, user_factory):
        """Test if users are created correctly"""

        email = "user1@test.com"
        password = "password"
        test_user = user_factory.create(email=email, password=password)

        assert test_user.email == email
        assert test_user.check_password(password)
        assert test_user.is_superuser is False
        assert test_user.is_staff is False
        assert test_user.is_active is True
        assert test_user.profile is not None
        assert test_user.profile.user_id == test_user.id

    def test_superuser_creation(self, user_factory):
        """Test if an admin user is created correctly"""

        email = "admin@test.com"
        password = "password"
        test_user = user_factory.create(email=email, password=password, is_superuser=True)

        assert test_user.email == email
        assert test_user.check_password(password)
        assert test_user.is_superuser is True
        assert test_user.is_staff is True
        assert test_user.is_active is True
        assert test_user.profile is not None
        assert test_user.profile.user_id == test_user.id


@pytest.mark.django_db
class TestUserRegistration:
    """Test suite for user registration"""

    def test_valid_registration(self, client):
        """Test if a user can register successfully"""
        url = reverse("register")
        redirect_url = reverse("dashboard")

        data = {
            "email": "user1@test.com",
            "password1": "password",
            "password2": "password",
        }

        response = client.post(url, data)

        assert response.status_code == 302
        assert response.url == redirect_url

        assert CustomUser.objects.filter(email=data["email"]).exists()

        assert response.wsgi_request.user.is_authenticated
        assert response.wsgi_request.user.email == data["email"]

    @pytest.mark.parametrize(
        "email, password1, password2, error_field",
        [
            ("invalidemail", "password", "password", "email"),
            ("", "password", "password", "email"),
            ("user@test.com", "password", "1234", "password2"),
        ],
    )
    def test_invalid_registration(self, client, email, password1, password2, error_field):
        """Test user registration with invalid data and check form errors properly."""
        url = reverse("register")

        data = {
            "email": email,
            "password1": password1,
            "password2": password2,
        }

        response = client.post(url, data)

        # Ensure form reloads on failure
        assert response.status_code == 200

        # Ensure user is NOT created in the database
        assert not CustomUser.objects.filter(email=email).exists()

        # Check if the error is in the correct field
        assert error_field in response.context["form"].errors

    def test_duplicate_user_registration(self, client):
        """Test that duplicate users cannot register with the same email"""
        email = "user1@test.com"
        password = "password"

        CustomUser.objects.create_user(email=email, password=password)

        url = reverse("register")
        data = {
            "email": email,
            "password1": password,
            "password2": password,
        }
        response = client.post(url, data)

        assert response.status_code == 200
        assert "email" in response.context["form"].errors
        assert CustomUser.objects.filter(email=email).count() == 1
        assert "User with this Email already exists." in response.context["form"].errors["email"]


@pytest.mark.django_db
class TestUserLogin:
    """Test suite for user login"""

    def test_valid_login(self, client):
        """Test if a user can log in successfully"""
        url = reverse("login")
        redirect_url = reverse("dashboard")
        email = "user1@test.com"
        password = "password"

        CustomUser.objects.create_user(email=email, password=password)
        assert CustomUser.objects.filter(email=email).exists()

        data = {
            "email": email,
            "password1": password
        }

        response = client.post(url, {"username": email, "password": password}, follow=True)

        assert response.status_code == 200
        assert response.redirect_chain[-1][0] == redirect_url

        assert response.wsgi_request.user.is_authenticated
        assert response.wsgi_request.user.email == data["email"]

    @pytest.mark.parametrize(
        "email, password, error_field",
        [
            ("test@test.com", "1234", "__all__"),
            ("user1@test.com", "1234", "__all__"),
            ("", "1234", "username"),
            ("user1@test.com", "", "password"),
        ],
    )
    def test_invalid_login(self, client, django_user_model, email, password, error_field):
        """Test login failures with incorrect credentials"""
        django_user_model.objects.create_user(email="user1@test.com", password="password")

        url = reverse("login")
        response = client.post(url, {"username": email, "password": password})

        assert response.status_code == 200
        assert not response.wsgi_request.user.is_authenticated
        assert error_field in response.context["form"].errors

    def test_logout(self, client, django_user_model):
        """Test that user can log out successfully"""
        email = "user1@test.com"
        password = "password"
        django_user_model.objects.create_user(email=email, password=password)
        client.login(email=email, password=password)

        url = reverse("logout")
        response = client.get(url)

        assert response.status_code == 302

        assert not response.wsgi_request.user.is_authenticated
