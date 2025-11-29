from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# ===============================
# CONTACT MODEL (Request + Accept)
# ===============================
class Contact(models.Model):
    owner   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_contacts")
    visitor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contact_user")

    status      = models.CharField(max_length=10, default="pending")  # pending / accepted

    call_count  = models.PositiveIntegerField(default=0)
    email_count = models.PositiveIntegerField(default=0)
    note_count  = models.PositiveIntegerField(default=0)

    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner} ← {self.visitor} [{self.status}]"


# ===============================
# NOTE MODEL
# ===============================
class ContactNote(models.Model):
    contact     = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="notes")
    text        = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note-{self.id}"


# ===============================
# NOTIFICATION SYSTEM MODEL
# ===============================
class Notification(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    message     = models.CharField(max_length=255)
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
