import requests
from abc import ABC, abstractmethod
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from django.db import models
from ..models import NotificationLog, SparePart, MaintenanceTask


class Notifier(ABC):
    @abstractmethod
    def send(self, customer, message: str, task=None):
        pass


class EmailNotifier(Notifier):
    def send(self, customer, message: str, task=None):
        if not customer.email:
            return False
        try:
            send_mail(
                subject="Asansör Bakım Bildirimi",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer.email],
                fail_silently=False,
            )
            NotificationLog.objects.create(
                customer=customer, task=task, channel='email',
                message=message, status='success'
            )
            if task:
                task.notification_sent = True
                task.save()
            return True
        except Exception as e:
            NotificationLog.objects.create(
                customer=customer, task=task, channel='email',
                message=message, status='failed', error_message=str(e)
            )
            return False


class TelegramNotifier(Notifier):
    def send(self, customer, message: str, task=None):
        if not customer.telegram_id or not settings.TELEGRAM_BOT_TOKEN:
            return False
        try:
            url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {'chat_id': customer.telegram_id, 'text': message, 'parse_mode': 'HTML'}
            response = requests.post(url, data=data)
            response.raise_for_status()

            NotificationLog.objects.create(
                customer=customer, task=task, channel='telegram',
                message=message, status='success'
            )
            if task:
                task.notification_sent = True
                task.save()
            return True
        except Exception as e:
            NotificationLog.objects.create(
                customer=customer, task=task, channel='telegram',
                message=message, status='failed', error_message=str(e)
            )
            return False


class WhatsAppNotifier(Notifier):
    def send(self, customer, message: str, task=None):
        if not customer.phone:
            return False
        clean_phone = customer.phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        link = f"https://wa.me/{clean_phone}?text={requests.utils.quote(message)}"
        
        NotificationLog.objects.create(
            customer=customer, task=task, channel='whatsapp',
            message=message, status='success'
        )
        if task:
            task.notification_sent = True
            task.save()
        
        return link


def create_critical_stock_notifications():
    """Kritik stok seviyesindeki parçalar için bildirim oluştur"""
    critical_parts = SparePart.objects.filter(quantity__lt=models.F('min_stock'))
    
    for part in critical_parts:
        exists = NotificationLog.objects.filter(
            notification_type='critical_stock',
            object_id=part.id,
            is_read=False
        ).exists()
        
        if not exists:
            NotificationLog.objects.create(
                notification_type='critical_stock',
                content_type=ContentType.objects.get_for_model(SparePart),
                object_id=part.id,
                message=f"{part.name} ({part.part_code}) stok seviyesi kritik! Mevcut: {part.quantity}, Minimum: {part.min_stock}",
                status='success',
                is_read=False
            )


def create_upcoming_task_notifications():
    """1 ay içinde yaklaşan ve bildirilmemiş görevler için bildirim oluştur"""
    one_month_later = timezone.now().date() + timedelta(days=30)
    
    upcoming_tasks = MaintenanceTask.objects.filter(
        status='pending',
        notification_sent=False,
        start_datetime__date__lte=one_month_later
    )

    for task in upcoming_tasks:
        exists = NotificationLog.objects.filter(
            notification_type='task_reminder',
            object_id=task.id,
            is_read=False
        ).exists()
        
        if not exists:
            NotificationLog.objects.create(
                notification_type='task_reminder',
                content_type=ContentType.objects.get_for_model(MaintenanceTask),
                object_id=task.id,
                message=f"{task.elevator.serial_number} için {task.get_task_type_display()} yaklaşan görev.",
                status='success',
                is_read=False
            )