from .models import NotificationLog
from .services.notification_service import create_critical_stock_notifications, create_upcoming_task_notifications

def unread_notifications(request):
    if request.user.is_authenticated:
        # Her istekte kritik stok ve yaklaşan görev bildirimlerini otomatik kontrol et
        create_critical_stock_notifications()
        create_upcoming_task_notifications()

        unread_count = NotificationLog.objects.filter(is_read=False).count()
        return {'unread_count': unread_count}
    return {'unread_count': 0}