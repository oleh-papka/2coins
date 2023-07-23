from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE)
    email = models.EmailField(max_length=500,
                              blank=False,
                              null=False)
    username = models.CharField(max_length=200,
                                blank=False,
                                null=False)
    bio = models.TextField(null=True,
                           blank=True)
    main_currency = models.ForeignKey('budget.Currency',
                                      null=True,
                                      blank=True,
                                      default=None,
                                      on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.user)
