import re
from datetime import date
from django.core.exceptions import ValidationError


def validate_username(value):
    """
    اعتبارسنجی نام کاربری
    - حداقل 3 کاراکتر
    - حداکثر 50 کاراکتر
    - فقط حروف، اعداد و آندرلاین
    - نباید با عدد شروع شود
    """
    if not value or value.strip() == '':
        raise ValidationError("نام کاربری نمی‌تواند خالی باشد")
    
    if len(value) < 3:
        raise ValidationError("نام کاربری باید حداقل 3 کاراکتر باشد")
    
    if len(value) > 50:
        raise ValidationError("نام کاربری نمی‌تواند بیشتر از 50 کاراکتر باشد")
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', value):
        raise ValidationError(
            "نام کاربری فقط می‌تواند شامل حروف، اعداد و آندرلاین باشد و نباید با عدد شروع شود"
        )


def validate_task_title(value):
    """
    اعتبارسنجی عنوان تسک
    - نباید خالی باشد
    - حداکثر 200 کاراکتر
    """
    if not value or value.strip() == '':
        raise ValidationError("عنوان تسک نمی‌تواند خالی باشد")
    
    if len(value) > 200:
        raise ValidationError("عنوان تسک نمی‌تواند بیشتر از 200 کاراکتر باشد")


def validate_task_description(value):
    """
    اعتبارسنجی توضیحات تسک
    - حداکثر 1000 کاراکتر
    """
    if value and len(value) > 1000:
        raise ValidationError("توضیحات نمی‌تواند بیشتر از 1000 کاراکتر باشد")


def validate_due_date(value):
    """
    اعتبارسنجی تاریخ ددلاین
    - نباید از تاریخ امروز کوچکتر باشد
    """
    if value:
        today = date.today()
        if value < today:
            raise ValidationError("تاریخ ددلاین نمی‌تواند از تاریخ امروز کوچکتر باشد")


def validate_user_exists(user_id):
    """
    اعتبارسنجی وجود کاربر
    """
    from .models import User
    try:
        user = User.objects.get(id=user_id)
        return user
    except User.DoesNotExist:
        raise ValidationError("کاربر مورد نظر یافت نشد")


def sanitize_input(value):
    """
    پاک‌سازی ورودی از کاراکترهای مخرب
    """
    if not value:
        return value
    
    # حذف تگ‌های HTML
    import html
    sanitized = html.escape(str(value))
    
    return sanitized


def validate_task_data(data):
    """
    اعتبارسنجی کامل داده‌های تسک
    """
    errors = {}
    
    # اعتبارسنجی عنوان
    try:
        validate_task_title(data.get('title', ''))
    except ValidationError as e:
        errors['title'] = str(e)
    
    # اعتبارسنجی توضیحات
    try:
        validate_task_description(data.get('description', ''))
    except ValidationError as e:
        errors['description'] = str(e)
    
    # اعتبارسنجی تاریخ
    due_date = data.get('due_date')
    if due_date:
        try:
            validate_due_date(due_date)
        except ValidationError as e:
            errors['due_date'] = str(e)
    
    return errors