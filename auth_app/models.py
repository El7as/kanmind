from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models



class CustomUserManager(BaseUserManager):

    """
    Custom manager for the User model that uses email instead of username
    as the unique identifier.

    Responsibilities:
        - create_user: Creates a regular user with email + password.
        - create_superuser: Creates a superuser with required flags.

    Notes:
        - Ensures email is always provided.
        - Normalizes email before saving.
        - Uses Django's built-in password hashing.
    """

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):

        """
        Create and return a regular user.

        Args:
            email (str): The user's email address (required).
            password (str): Raw password (hashed automatically).
            extra_fields (dict): Additional model fields.

        Raises:
            ValueError: If email is missing.

        Returns:
            User: The created user instance.
        """

        if not email:
            raise ValueError("Email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):

        """
        Create and return a superuser.

        Ensures:
            - is_staff=True
            - is_superuser=True

        Raises:
            ValueError: If required flags are missing.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):

    """
    Custom user model that replaces the username field with email.

    Changes:
        - username removed
        - email becomes the unique login identifier
        - first_name and last_name kept for display purposes

    Attributes:
        first_name (str): Optional first name.
        last_name (str): Optional last name.
        email (str): Unique email used for authentication.

    Authentication:
        USERNAME_FIELD = 'email'
        REQUIRED_FIELDS = []  (no additional fields required for createsuperuser)

    Manager:
        objects = CustomUserManager
    """

    username = None
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

