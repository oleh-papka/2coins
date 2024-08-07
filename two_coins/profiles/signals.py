from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, CustomUser


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


@receiver(post_delete, sender=CustomUser)
def delete_user_profile(sender, instance, **kwargs):
    if instance.profile:
        instance.profile.delete()
