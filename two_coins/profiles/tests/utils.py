import pytest

from profiles.models import CustomUser

DEFAULT_USER_DATA = {
    "email": "user@test.com",
    "password": "password",
}


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


@pytest.fixture
def default_user(user_factory):
    """Fixture that returns the default user"""
    return user_factory.create(**DEFAULT_USER_DATA)
