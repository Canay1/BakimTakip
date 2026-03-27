from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, time
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType



class Customer(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Ad")
    last_name = models.CharField(max_length=100, verbose_name="Soyad")
    company = models.CharField(max_length=150, blank=True, null=True, verbose_name="Firma")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    email = models.EmailField(blank=True, null=True, verbose_name="E-posta")
    telegram_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telegram ID")
    preferred_channel = models.CharField(
        max_length=20,
        choices=[
            ('email', 'E-posta'),
            ('whatsapp', 'WhatsApp'),
            ('telegram', 'Telegram'),
            ('phone', 'Telefon Araması'),
        ],
        default='whatsapp',
        verbose_name="Tercih Edilen Kanal"
    )
    notes = models.TextField(blank=True, verbose_name="Notlar")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Müşteri"
        verbose_name_plural = "Müşteriler"
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Elevator(models.Model):
    serial_number = models.CharField(max_length=50, unique=True, verbose_name="Seri No")
    location = models.TextField(verbose_name="Konum")
    install_date = models.DateField(verbose_name="Kurulum Tarihi")
    last_maintenance = models.DateField(null=True, blank=True, verbose_name="Son Bakım")
    status = models.CharField(max_length=20, choices=[('active', 'Aktif'), ('fault', 'Arızalı')], default='active')
    
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Müşteri"
    )
    notes = models.TextField(blank=True, verbose_name="Notlar")

    def __str__(self):
        return self.serial_number


class MaintenanceTask(models.Model):
    TASK_TYPE = [('periodic', 'Periyodik'), ('fault', 'Arıza')]
    STATUS = [('pending', 'Bekliyor'), ('completed', 'Tamamlandı')]

    elevator = models.ForeignKey(Elevator, on_delete=models.CASCADE, verbose_name="Asansör")
    task_type = models.CharField(max_length=20, choices=TASK_TYPE, verbose_name="İş Türü")
    
    due_date = models.DateField(null=True, blank=True, verbose_name="Tarih (Opsiyonel)")
    start_datetime = models.DateTimeField(null=True, blank=True, verbose_name="Başlangıç Saati")
    end_datetime = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş Saati")
    all_day = models.BooleanField(default=False, verbose_name="Bütün Gün")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Atanan")
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    notes = models.TextField(blank=True)
    notification_sent = models.BooleanField(default=False, verbose_name="Bildirim Gönderildi mi?")

    # Generic Relation - Reverse lookup için
    notification_logs = GenericRelation('NotificationLog')

    class Meta:
        ordering = ['start_datetime', 'due_date']

    def __str__(self):
        return f"{self.elevator} - {self.get_task_type_display()}"


class SparePart(models.Model):
    part_code = models.CharField(max_length=30, unique=True, verbose_name="Parça Kodu")
    name = models.CharField(max_length=100, verbose_name="Parça Adı")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Stok")
    min_stock = models.PositiveIntegerField(default=5, verbose_name="Kritik Seviye")
    barcode = models.CharField(max_length=50, unique=True, verbose_name="Barkod")

    # Generic Relation - Reverse lookup için
    notification_logs = GenericRelation('NotificationLog')

    def __str__(self):
        return f"{self.part_code} - {self.name}"

    @property
    def is_critical(self):
        return self.quantity < self.min_stock


class NotificationLog(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(MaintenanceTask, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.CharField(max_length=20, choices=Customer._meta.get_field('preferred_channel').choices, null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[('success', 'Başarılı'), ('failed', 'Başarısız')], default='success')
    sent_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False, verbose_name="Okundu mu?")

    notification_type = models.CharField(
        max_length=30,
        choices=[
            ('task_reminder', 'Yaklaşan Görev'),
            ('critical_stock', 'Kritik Stok'),
        ],
        default='task_reminder'
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Bildirim Logu"
        verbose_name_plural = "Bildirim Logları"
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.notification_type} - {self.sent_at.strftime('%d.%m %H:%M')}"