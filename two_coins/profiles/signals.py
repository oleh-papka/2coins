from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User, dispatch_uid='save_new_profile')
def save_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile(user=instance,
                          username=instance.username,
                          email=instance.email)
        profile.save()


@receiver(post_save, sender=Profile, dispatch_uid='update_user')
def update_user(sender, instance, created, **kwargs):
    user = instance.user

    if not created:
        user.username = instance.username
        user.email = instance.email

        user.save()


@receiver(post_delete, sender=Profile, dispatch_uid='delete_user')
def delete_user(sender, instance, **kwargs):
    try:
        user = instance.user
        user.delete()
    except:
        pass
