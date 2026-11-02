"""
URL Configuration for To-Do List API

این فایل شامل تمام اندپوینت‌های API برای مدیریت کاربران و تسک‌ها است.

اندپوینت‌ها:
    - POST   /api/set-user/              : انتخاب یا ایجاد کاربر
    - GET    /api/users/                 : لیست تمام کاربران
    - GET    /api/tasks/                 : لیست تسک‌های کاربر
    - POST   /api/tasks/create/          : ایجاد تسک جدید
    - POST   /api/tasks/<id>/update/     : ویرایش تسک
    - POST   /api/tasks/<id>/toggle-complete/ : تغییر وضعیت انجام
    - DELETE /api/tasks/<id>/delete/    : حذف تسک
"""

from django.urls import path
from . import views

# backend/todo_app/urls.py
urlpatterns = [
    # SPECIFIC patterns FIRST
    path('tasks/create/', views.create_task, name='create-task'),  # ← More specific
    path('tasks/<int:task_id>/update/', views.update_task, name='update-task'),
    path('tasks/<int:task_id>/toggle-complete/', views.toggle_complete, name='toggle-complete'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete-task'),
    
    # GENERAL pattern LAST
    path('tasks/', views.get_tasks, name='get-tasks'),  # ← Catch-all for /tasks/
    
    path('set-user/', views.set_user, name='set-user'),
    path('users/', views.get_users, name='get-users'),
]