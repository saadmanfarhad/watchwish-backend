from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

# Create your models here.
class CustomUser(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(max_length=30, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True, null=True)
    avatar = models.CharField(_('avatar'), max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    about = models.TextField(_('about'), blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Watchlist(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'media_id'], name='unique watchlist media')
        ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    media_id = models.IntegerField(blank=False, null=False)
    media_type = models.CharField(max_length=30, blank=False, null=False)
    watched = models.BooleanField(default=False, blank=False, null=False)

class Review(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'media_id'], name='unique review media')
        ]
    user = models.ForeignKey(CustomUser, blank=False, null=False, on_delete=models.CASCADE)
    media_id = models.IntegerField(blank=False, null=False)
    review = models.TextField(blank=False, null=False)
