from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Contact(models.Model):
    owner       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_contacts")
    visitor     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contact_user")

    status      = models.CharField(max_length=10, default="pending")  # 🔥 NEW FIELD

    call_count  = models.PositiveIntegerField(default=0)
    email_count = models.PositiveIntegerField(default=0)
    note_count  = models.PositiveIntegerField(default=0)

    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner} ← {self.visitor} [{self.status}]"


class ContactNote(models.Model):
    contact     = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="notes")
    text        = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note-{self.id}"
