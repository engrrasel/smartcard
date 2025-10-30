from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """🟢 নতুন ইউজার তৈরি হলে তার জন্য একটি প্রোফাইল তৈরি করো।"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """🟡 ইউজার আপডেট হলে তার প্রোফাইলও আপডেট করে রাখো (যদি থাকে)।"""
    profile = instance.userprofile_set.first()  # ✅ ForeignKey হলে .userprofile_set ব্যবহার করতে হয়
    if profile:
        profile.save()
