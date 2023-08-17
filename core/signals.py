from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import GroupChatRoom



@receiver(post_save, sender=GroupChatRoom)
def user_created(sender, instance, created, **kwargs):
   if created:
        instance.admin_users.add(instance.created_by)