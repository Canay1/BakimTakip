from django.urls import path
from .views import (
    dashboard,
    ElevatorListView,
    ElevatorCreateView,
    ElevatorUpdateView,
    TaskListView,
    TaskCreateView,
    TaskUpdateView,
    PartListView,
    PartCreateView,
    PartUpdateView,
    task_api,
    day_detail,
    CustomerListView,
    CustomerCreateView,
    CustomerUpdateView,
    NotificationLogListView,
    ElevatorDeleteView,
    TaskDeleteView,
    CustomerDeleteView,
    NotificationLogDeleteView,
    PartDeleteView,
    notify_customer,
    mark_task_as_notified,
    mark_task_as_not_notified,
    mark_all_notifications_read,
)

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),

    path('elevators/',          ElevatorListView.as_view(),   name='elevators'),
    path('elevators/create/', ElevatorCreateView.as_view(), name='elevator_create'),
    path('elevators/<int:pk>/update/', ElevatorUpdateView.as_view(), name='elevator_update'),
    path('tasks/',              TaskListView.as_view(),       name='tasks'),
    path('tasks/create/',       TaskCreateView.as_view(),     name='task_create'),
    path('tasks/<int:pk>/update/', TaskUpdateView.as_view(),  name='task_update'),

    path('parts/',              PartListView.as_view(),       name='parts'),
    path('parts/create/',       PartCreateView.as_view(),     name='part_create'),
    path('parts/<int:pk>/update/', PartUpdateView.as_view(),  name='part_update'),

    path('api/tasks/', task_api, name='task_api'),
    path('calendar/day/<str:date_str>/', day_detail, name='day_detail'),

    path('customers/', CustomerListView.as_view(), name='customers'),
    path('customers/create/', CustomerCreateView.as_view(), name='customer_create'),
    path('customers/<int:pk>/update/', CustomerUpdateView.as_view(), name='customer_update'),

    path('notifications/', NotificationLogListView.as_view(), name='notification_log'),   # ← BU SATIRI EKLE


    path('elevators/<int:pk>/delete/', ElevatorDeleteView.as_view(), name='elevator_delete'),




    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    path('parts/<int:pk>/delete/', PartDeleteView.as_view(), name='part_delete'),



    path('customers/<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer_delete'),
    path('notifications/<int:pk>/delete/', NotificationLogDeleteView.as_view(), name='notification_log_delete'),
    path('customers/<int:pk>/update/', CustomerUpdateView.as_view(), name='customer_update'),
    path('tasks/<int:task_id>/notify/', notify_customer, name='notify_customer'),
    path('tasks/<int:task_id>/mark_notified/', mark_task_as_notified, name='mark_task_as_notified'),
    path('tasks/<int:task_id>/mark_not_notified/', mark_task_as_not_notified, name='mark_task_as_not_notified'),



    path('notifications/mark-all-read/', mark_all_notifications_read, name='mark_all_notifications_read'),
]