from django import forms
from .models import MaintenanceTask, Elevator, SparePart, Customer
from datetime import date
from django.utils import timezone

class ElevatorForm(forms.ModelForm):
    class Meta:
        model = Elevator
        fields = ['serial_number', 'location', 'install_date', 'last_maintenance', 'status', 'customer', 'notes']
        widgets = {
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'install_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'last_maintenance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Asansör hakkında ek notlar, özel talepler, bakım geçmişi vs...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Zorunlu alanlar
        self.fields['serial_number'].required = True
        self.fields['location'].required = True
        self.fields['install_date'].required = True
        self.fields['status'].required = True

        # Düzenleme modunda tarihleri doğru formatta yükle (YYYY-MM-DD)
        instance = kwargs.get('instance')
        if instance:
            if instance.install_date:
                self.initial['install_date'] = instance.install_date.isoformat()
            if instance.last_maintenance:
                self.initial['last_maintenance'] = instance.last_maintenance.isoformat()

class TaskForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTask
        fields = [
            'elevator',
            'task_type',
            'start_datetime',
            'end_datetime',
            'all_day',
            'assigned_to',
            'status',
            'notes',
            'notification_sent'
        ]
        widgets = {
            'elevator': forms.Select(attrs={'class': 'form-select'}),
            'task_type': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_datetime': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_datetime': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'all_day': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notification_sent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        self.fields['elevator'].required = True
        self.fields['task_type'].required = True
        self.fields['start_datetime'].required = True

        if instance and instance.pk:   # DÜZENLEME MODU
            if instance.all_day:
                # All Day → sadece tarih göster
                self.fields['start_datetime'].widget = forms.DateInput(
                    attrs={'type': 'date', 'class': 'form-control'}
                )
                self.fields['end_datetime'].widget = forms.DateInput(
                    attrs={'type': 'date', 'class': 'form-control'}
                )

                if instance.start_datetime:
                    # Türkiye saatine çevir ve sadece tarih al
                    local_date = timezone.localtime(instance.start_datetime).date()
                    self.initial['start_datetime'] = local_date.isoformat()

                if instance.end_datetime:
                    local_date = timezone.localtime(instance.end_datetime).date()
                    self.initial['end_datetime'] = local_date.isoformat()

            else:
                # Normal mod → saat + tarih göster
                self.fields['start_datetime'].widget = forms.DateTimeInput(
                    attrs={'type': 'datetime-local', 'class': 'form-control'},
                    format='%Y-%m-%dT%H:%M'
                )
                self.fields['end_datetime'].widget = forms.DateTimeInput(
                    attrs={'type': 'datetime-local', 'class': 'form-control'},
                    format='%Y-%m-%dT%H:%M'
                )

                if instance.start_datetime:
                    local_dt = timezone.localtime(instance.start_datetime)
                    self.initial['start_datetime'] = local_dt.strftime('%Y-%m-%dT%H:%M')

                if instance.end_datetime:
                    local_dt = timezone.localtime(instance.end_datetime)
                    self.initial['end_datetime'] = local_dt.strftime('%Y-%m-%dT%H:%M')


class PartForm(forms.ModelForm):
    class Meta:
        model = SparePart
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'part_code': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'preferred_channel': forms.Select(attrs={
                'class': 'form-select'
            }),
            # Diğer alanlara dokunmuyoruz
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telegram_id': forms.TextInput(attrs={'class': 'form-control'}),

        }