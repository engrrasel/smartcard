from app_contacts.models import Notification
from .models import ContactRequest

def notif_context(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(user=request.user, is_read=False)
        return {
            "unread_count": unread.count(),
            "unread_notifications": unread
        }
    return {"unread_count": 0, "unread_notifications": []}


def pending_request_count(request):
    if request.user.is_authenticated:
        count = ContactRequest.objects.filter(receiver=request.user, status="pending").count()
        return {"pending_request_count": count}
    return {"pending_request_count": 0}
