from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *

# Declares that the function would handle the post_save signal for the User model
# sender: the model that sent the signal
# instance: the model instance that was saved
# created: a boolean that tells whether it created a new instance or just updated one

@receiver(signal=post_save, sender=Progress)
def checkCourseComplete(sender, instance :Progress, created, **kwargs):
    if created:
        enrollment = instance.getEnrollment()
        completed, total = enrollment.getProgress()

        if completed == total:
            enrollment.is_complete = True
            enrollment.save()




