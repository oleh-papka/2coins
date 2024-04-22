from django.contrib.auth.models import User
from django.db import models

from budget.models import Category


class Profile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE)
    email = models.EmailField(max_length=500,
                              blank=False,
                              null=False)
    username = models.CharField(max_length=200,
                                blank=False,
                                null=False)
    main_currency = models.ForeignKey('budget.Currency',
                                      null=True,
                                      blank=True,
                                      default=None,
                                      on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        Category.objects.create(name='Other',
                                cat_type=Category.OTHER,
                                profile=self,
                                icon="fa-solid fa-ellipsis",
                                color="#787878")

        Category.objects.create(name='Money transfer',
                                cat_type=Category.TRANSFER,
                                profile=self,
                                icon="fa-solid fa-arrow-right-arrow-left",
                                color="#34eba1")
