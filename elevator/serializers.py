from rest_framework import serializers
from .models import MaintenanceTask

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceTask
        fields = [
            'id',
            'elevator',
            'task_type',
            'due_date',
            'start_datetime',
            'end_datetime',
            'all_day',
            'status',
            'notes',
        ]