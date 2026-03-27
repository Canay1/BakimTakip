from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db import models
from .models import Elevator, MaintenanceTask, SparePart, Customer, NotificationLog
from .forms import TaskForm, ElevatorForm, PartForm, CustomerForm
from .serializers import TaskSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import date, timedelta
from django.views.generic import UpdateView
from django.shortcuts import get_object_or_404
from datetime import datetime, time
from django.utils.dateparse import parse_date
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.utils.dateparse import parse_datetime
from .services.notification_service import EmailNotifier, TelegramNotifier, WhatsAppNotifier
from django.views.generic.edit import DeleteView
from django.http import JsonResponse
from django.template.loader import render_to_string
from .services.notification_service import EmailNotifier, TelegramNotifier, WhatsAppNotifier
from .models import Customer





class SortableListView(ListView):
    """Tıklanabilir sütun sıralama için ortak mixin"""
    ordering = None

    def get_ordering(self):
        order_by = self.request.GET.get('order_by')
        direction = self.request.GET.get('direction', 'asc')

        if order_by:
            if direction == 'desc':
                return f'-{order_by}'
            return order_by
        return self.ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_order'] = self.request.GET.get('order_by')
        context['current_dir'] = self.request.GET.get('direction', 'asc')
        return context








@login_required
def dashboard(request):
    elevators = Elevator.objects.count()
    pending_tasks = MaintenanceTask.objects.filter(status='pending').count()
    critical_parts = SparePart.objects.filter(quantity__lt=models.F('min_stock')).count()
    
    # Otomatik bakım planlama butonu için
    if request.method == 'POST' and 'auto_plan' in request.POST:
        planned = 0
        for elev in Elevator.objects.all():
            if not elev.last_maintenance or (date.today() - elev.last_maintenance).days > 30:
                MaintenanceTask.objects.create(
                    elevator=elev,
                    task_type='periodic',
                    due_date=date.today() + timedelta(days=7),
                    status='pending'
                )
                planned += 1
        messages.success(request, f"{planned} yeni bakım görevi oluşturuldu!")
        return redirect('dashboard')
    
    context = {
        'elevators': elevators,
        'pending_tasks': pending_tasks,
        'critical_parts': critical_parts,
    }
    return render(request, 'dashboard.html', context)

class ElevatorListView(LoginRequiredMixin, SortableListView):
    model = Elevator
    template_name = 'elevators.html'
    context_object_name = 'elevators'
    ordering = ['serial_number']







class ElevatorCreateView(LoginRequiredMixin, CreateView):
    model = Elevator
    form_class = ElevatorForm
    template_name = 'elevator_form.html'
    success_url = reverse_lazy('elevators')

    def form_valid(self, form):
        messages.success(self.request, "Asansör başarıyla eklendi.")
        return super().form_valid(form)
        
        
        
        
class TaskListView(SortableListView):
    model = MaintenanceTask
    template_name = 'tasks.html'
    context_object_name = 'tasks'
    ordering = ['due_date']

    def get_queryset(self):
        return super().get_queryset().select_related('elevator', 'assigned_to', 'elevator__customer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        context['pending_notifications'] = [] 
        return context

class TaskCreateView(CreateView):
    model = MaintenanceTask
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        task = form.save(commit=False)
        # Eğer due_date boş geldiyse start_datetime'dan tarih çıkar
        if not task.due_date and task.start_datetime:
            task.due_date = task.start_datetime.date()
        task.save()
        messages.success(self.request, "Görev başarıyla oluşturuldu.")
        return super().form_valid(form)

class PartListView(LoginRequiredMixin, SortableListView):
    model = SparePart
    template_name = 'parts.html'
    context_object_name = 'parts'
    ordering = ['part_code']

class PartCreateView(LoginRequiredMixin, CreateView):
    model = SparePart
    form_class = PartForm
    template_name = 'part_form.html'
    success_url = reverse_lazy('parts')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_api(request):
    tasks = MaintenanceTask.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


class ElevatorUpdateView(UpdateView):
    model = Elevator
    form_class = ElevatorForm
    template_name = 'elevator_form.html'
    success_url = reverse_lazy('elevators')

    def form_valid(self, form):
        messages.success(self.request, "Asansör başarıyla güncellendi.")
        return super().form_valid(form)

class TaskUpdateView(UpdateView):
    model = MaintenanceTask
    form_class = TaskForm
    template_name = 'task_form.html'
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        task = form.save(commit=False)
        # due_date her zaman start_datetime'dan gelsin
        if task.start_datetime:
            task.due_date = task.start_datetime.date()
        task.save()
        messages.success(self.request, "Görev başarıyla güncellendi.")
        return super().form_valid(form)










class PartUpdateView(LoginRequiredMixin, UpdateView):
    model = SparePart
    form_class = PartForm
    template_name = 'part_form.html'
    success_url = reverse_lazy('parts')



@login_required
def day_detail(request, date_str):
    parsed_datetime = parse_datetime(date_str)

    if parsed_datetime is None:
        try:
            parsed_date = parse_date(date_str.split('T')[0])
            if parsed_date:
                selected_date = parsed_date
            else:
                raise Http404("Geçersiz tarih")
        except:
            raise Http404("Geçersiz tarih")
    else:
        selected_date = parsed_datetime.date()

    day_start = datetime.combine(selected_date, time.min)
    day_end = datetime.combine(selected_date, time.max)

    tasks = MaintenanceTask.objects.filter(
        models.Q(
            start_datetime__lte=day_end,
            end_datetime__gte=day_start
        )
        |
        models.Q(
            start_datetime__lte=day_end,
            end_datetime__isnull=True
        )
        |
        models.Q(
            due_date=selected_date
        )
    ).order_by('start_datetime')

    initial_data = {
        'start_datetime': f"{selected_date}T09:00",
    }

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            if not task.due_date and task.start_datetime:
                task.due_date = task.start_datetime.date()
            task.save()
            messages.success(request, f"{selected_date.strftime('%d.%m.%Y')} için görev eklendi!")
            return redirect('day_detail', date_str=selected_date.strftime('%Y-%m-%d'))
    else:
        form = TaskForm(initial=initial_data)

    return render(request, 'day_detail.html', {
        'selected_date': selected_date,
        'tasks': tasks,
        'form': form,
    })


class CustomerListView(SortableListView):
    model = Customer
    template_name = 'customers.html'
    context_object_name = 'customers'
    ordering = ['first_name']

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customer_form.html'
    success_url = reverse_lazy('customers')

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customer_form.html'
    success_url = reverse_lazy('customers')









class NotificationLogListView(SortableListView):
    model = NotificationLog
    template_name = 'notification_log.html'
    context_object_name = 'logs'
    ordering = ['-sent_at']

    def get_queryset(self):
        # Tüm bildirimleri getir ama okunmamışları öne çıkar
        return super().get_queryset().select_related('customer', 'task')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Okunmamış bildirim sayısı
        context['unread_count'] = NotificationLog.objects.filter(is_read=False).count()
        return context









@login_required
def mark_all_notifications_read(request):
    NotificationLog.objects.filter(is_read=False).update(is_read=True)
    return redirect('notification_log')






















@login_required
def send_notification(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer = Customer.objects.get(id=data['customer_id'])
        task = MaintenanceTask.objects.get(id=data['task_id'])
        message = data['message']
        channel = data['channel']

        if channel == 'email':
            success = EmailNotifier().send(customer, message, task)
        elif channel == 'telegram':
            success = TelegramNotifier().send(customer, message, task)
        elif channel == 'whatsapp':
            link = WhatsAppNotifier().send(customer, message, task)
            return JsonResponse({'success': True, 'whatsapp_link': link})

        return JsonResponse({'success': success})
    return JsonResponse({'success': False})













class ElevatorDeleteView(DeleteView):
    model = Elevator
    success_url = reverse_lazy('elevators')

    def get(self, request, *args, **kwargs):
        # Güvenlik: Direkt GET ile silme sayfasına gitmesin
        return redirect('elevators')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Asansör başarıyla silindi.")
        return super().delete(request, *args, **kwargs)

class TaskDeleteView(DeleteView):
    model = MaintenanceTask
    success_url = reverse_lazy('tasks')

    def get(self, request, *args, **kwargs):
        return redirect('tasks')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Görev başarıyla silindi.")
        return super().delete(request, *args, **kwargs)

class CustomerDeleteView(DeleteView):
    model = Customer
    success_url = reverse_lazy('customers')

    def get(self, request, *args, **kwargs):
        return redirect('customers')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Müşteri başarıyla silindi.")
        return super().delete(request, *args, **kwargs)

class NotificationLogDeleteView(DeleteView):
    model = NotificationLog
    success_url = reverse_lazy('notification_log')

    def get(self, request, *args, **kwargs):
        return redirect('notification_log')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Bildirim logu başarıyla silindi.")
        return super().delete(request, *args, **kwargs)

class PartDeleteView(DeleteView):
    model = SparePart
    success_url = reverse_lazy('parts')

    def get(self, request, *args, **kwargs):
        return redirect('parts')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Parça başarıyla silindi.")
        return super().delete(request, *args, **kwargs)




































@login_required
def notify_customer(request, task_id):
    task = get_object_or_404(MaintenanceTask, id=task_id)
    
    if not task.elevator.customer:
        return JsonResponse({'success': False, 'error': 'Bu göreve ait müşteri bulunamadı.'})

    customer = task.elevator.customer

    message_template = (
        f"Sayın {customer.get_full_name()}, "
        f"{task.elevator.serial_number} seri numaralı asansörünüzün "
        f"{task.get_task_type_display()} kaydı alınmıştır. "
        f"{task.start_datetime.strftime('%d.%m.%Y %H:%M')} tarihinde ekiplerimiz tarafınıza ulaşacaktır."
    )

    if request.method == 'POST':
        channel = request.POST.get('channel')
        custom_message = request.POST.get('message', message_template)

        if channel == 'whatsapp':
            link = WhatsAppNotifier().send(customer, custom_message, task)
            return JsonResponse({'success': True, 'whatsapp_link': link})

        elif channel == 'email':
            success = EmailNotifier().send(customer, custom_message, task)
        elif channel == 'telegram':
            success = TelegramNotifier().send(customer, custom_message, task)
        else:
            success = False

        return JsonResponse({'success': success})

    # GET isteği
    context = {
        'task': task,
        'customer': customer,
        'default_message': message_template,
    }
    html = render_to_string('notify_modal.html', context, request=request)
    return JsonResponse({'html': html})
























@login_required
def mark_task_as_notified(request, task_id):
    task = get_object_or_404(MaintenanceTask, id=task_id)
    task.notification_sent = True
    task.save()
    return JsonResponse({'success': True})

@login_required
def mark_task_as_not_notified(request, task_id):
    task = get_object_or_404(MaintenanceTask, id=task_id)
    task.notification_sent = False
    task.save()
    return JsonResponse({'success': True})