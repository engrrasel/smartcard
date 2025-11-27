from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()



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



class Contact(models.Model):
    owner       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_contacts", null=True, blank=True)
    visitor     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contact_user", null=True, blank=True)

    call_count  = models.PositiveIntegerField(default=0)
    email_count = models.PositiveIntegerField(default=0)
    note_count  = models.PositiveIntegerField(default=0)

    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner} → {self.visitor}"


class ContactNote(models.Model):
    contact     = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="notes")
    text        = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note-{self.id}"
