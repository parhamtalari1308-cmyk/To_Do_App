from django.utils import timezone
from datetime import datetime, date


def serialize_user(user):
    """
    تبدیل مدل User به دیکشنری JSON
    """
    return {
        'id': user.id,
        'username': user.username,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'task_count': user.get_task_count()
    }


def serialize_task(task):
    """
    تبدیل مدل Task به دیکشنری JSON
    """
    return {
        'id': task.id,
        'user': task.user.id,
        'user_username': task.user.username,
        'title': task.title,
        'description': task.description or '',
        'completed': task.completed,
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'is_overdue': task.is_overdue(),
        'status': task.get_status_display()
    }


def serialize_users(users):
    """
    تبدیل لیست کاربران به لیست دیکشنری‌ها
    """
    return [serialize_user(user) for user in users]


def serialize_tasks(tasks):
    """
    تبدیل لیست تسک‌ها به لیست دیکشنری‌ها
    """
    return [serialize_task(task) for task in tasks]


def deserialize_date(date_str):
    """
    تبدیل رشته تاریخ به شیء date
    """
    if not date_str:
        return None
    
    try:
        # فرمت: YYYY-MM-DD
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None


def deserialize_datetime(datetime_str):
    """
    تبدیل رشته تاریخ و زمان به شیء datetime
    """
    if not datetime_str:
        return None
    
    try:
        return datetime.fromisoformat(datetime_str)
    except (ValueError, TypeError):
        return None


def format_response(success=True, message='', data=None, errors=None):
    """
    فرمت‌دهی پاسخ استاندارد API
    """
    response = {
        'success': success,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    if errors is not None:
        response['errors'] = errors
    
    return response