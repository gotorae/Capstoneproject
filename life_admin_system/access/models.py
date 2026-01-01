
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class ChiefUnderwriter(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Enter a valid email")

        # Correct: pass the email to normalize_email
        email = self.normalize_email(email)

        # Correct: use self.model, not self(...)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Correct method name
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        # Defaults for a normal user
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        # Must be staff & superuser
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Administrator(AbstractBaseUser, PermissionsMixin):
    #user_id = models.CharField(max_length=5, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=30)
    dob = models.DateField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)

    date_created = models.DateTimeField(default=timezone.now)

    # Core flags Django expects
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = ChiefUnderwriter()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]  # prompted when creating superuser

    


    def __str__(self):
        return f"{self.first_name} {self.last_name}"



# Create your models here.
