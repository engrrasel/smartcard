from django.db import models
from django.conf import settings

class Contact(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='my_contacts',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    visitor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_requests',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
