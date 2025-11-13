from datetime import date
from .models import UserProfile

def reset_daily_views():
    today = date.today()
    UserProfile.objects.update(daily_views=0, last_viewed=today)
    print(f"[CRON JOB] ✅ Daily views reset successfully at {today}")
