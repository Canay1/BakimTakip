from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Elevator, MaintenanceTask, SparePart, 
    Customer, NotificationLog
)


@admin.register(Elevator)
class ElevatorAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'location_short', 'customer', 'install_date', 
                   'last_maintenance', 'status', 'has_customer')
    list_filter = ('status', 'install_date', 'customer')
    search_fields = ('serial_number', 'location', 'customer__first_name', 'customer__last_name')
    ordering = ('-install_date',)
    list_select_related = ('customer',)

    def location_short(self, obj):
        return (obj.location[:60] + '...') if len(obj.location) > 60 else obj.location
    location_short.short_description = "Konum"

    def has_customer(self, obj):
        return "✅" if obj.customer else "❌"
    has_customer.short_description = "Müşteri Var mı?"


@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ('elevator', 'task_type_display', 'due_date', 'start_time', 
                   'assigned_to', 'status_display', 'all_day')
    list_filter = ('task_type', 'status', 'due_date', 'all_day', 'assigned_to')
    search_fields = ('elevator__serial_number', 'notes', 'assigned_to__username')
    date_hierarchy = 'due_date'
    list_select_related = ('elevator', 'assigned_to')
    ordering = ('-due_date',)

    def task_type_display(self, obj):
        return obj.get_task_type_display()
    task_type_display.short_description = "İş Türü"

    def status_display(self, obj):
        colors = {'pending': 'warning', 'completed': 'success'}
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_display.short_description = "Durum"

    def start_time(self, obj):
        return obj.start_datetime.strftime("%H:%M") if obj.start_datetime else "-"
    start_time.short_description = "Başlangıç Saati"

    def all_day(self, obj):
        return "✅" if obj.all_day else "❌"
    all_day.short_description = "Bütün Gün"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'company', 'phone', 'email', 'preferred_channel_display', 'created_at')
    list_filter = ('preferred_channel', 'created_at')
    search_fields = ('first_name', 'last_name', 'company', 'phone', 'email', 'telegram_id')
    ordering = ('first_name', 'last_name')

    def full_name(self, obj):
        return obj.get_full_name()
    full_name.short_description = "Ad Soyad"

    def preferred_channel_display(self, obj):
        return obj.get_preferred_channel_display()
    preferred_channel_display.short_description = "Tercih Edilen Kanal"


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ('part_code', 'name', 'quantity', 'min_stock', 'critical_status', 'barcode')
    list_filter = ('quantity',)
    search_fields = ('part_code', 'name', 'barcode')
    ordering = ('part_code',)

    def critical_status(self, obj):
        if obj.is_critical:
            return format_html('<span style="color: red; font-weight: bold;">KRİTİK</span>')
        return format_html('<span style="color: green;">Normal</span>')
    critical_status.short_description = "Durum"




@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('sent_at', 'customer', 'channel', 'short_message', 'status_badge', 'task_link')
    list_filter = ('channel', 'status', 'sent_at')
    search_fields = ('customer__first_name', 'customer__last_name', 'message')
    date_hierarchy = 'sent_at'
    ordering = ('-sent_at',)
    list_select_related = ('customer', 'task')

    def short_message(self, obj):
        return obj.message[:80] + "..." if len(obj.message) > 80 else obj.message
    short_message.short_description = "Mesaj"

    def status_badge(self, obj):
        color = "success" if obj.status == "success" else "danger"
        return format_html('<span class="badge bg-{}">{}</span>', color, obj.get_status_display())
    status_badge.short_description = "Durum"

    def task_link(self, obj):
        if obj.task:
            url = reverse("admin:elevator_maintenancetask_change", args=[obj.task.id])
            return format_html('<a href="{}">Görev #{}</a>', url, obj.task.id)
        return "-"
    task_link.short_description = "İlgili Görev"