from .models import Contact, Notification

# 🔔 Notification counter
def notif_context(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(user=request.user, is_read=False)
        return {
            "unread_count": unread.count(),
            "unread_notifications": unread
        }
    return {"unread_count": 0, "unread_notifications": []}


# 🔥 Pending Request Counter (global count)
def pending_request_count(request):
    if request.user.is_authenticated:
        count = Contact.objects.filter(owner=request.user, status="pending").count()
        return {"pending_request_count": count}
    return {"pending_request_count": 0}
