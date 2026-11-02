from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator


class User(models.Model):
    """مدل کاربر"""
    username = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            MinLengthValidator(3, message="نام کاربری باید حداقل 3 کاراکتر باشد"),
            MaxLengthValidator(50, message="نام کاربری نمی‌تواند بیشتر از 50 کاراکتر باشد"),
            RegexValidator(
                regex='^[a-zA-Z][a-zA-Z0-9_]*$',
                message="نام کاربری فقط می‌تواند شامل حروف، اعداد و آندرلاین باشد و نباید با عدد شروع شود"
            )
        ],
        help_text="نام کاربری باید منحصر به فرد باشد",
        db_index=True  # ✅ ایندکس اضافه شد
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        db_table = 'users'
        ordering = ['username']
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        indexes = [
            models.Index(fields=['username']),  # ✅ ایندکس اضافه شد
        ]
    
    def __str__(self):
        return self.username
    
    def get_task_count(self):
        """تعداد تسک‌های کاربر"""
        return self.tasks.count()


class Task(models.Model):
    """مدل تسک"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        verbose_name="کاربر",
        db_index=True  # ✅ ایندکس اضافه شد
    )
    title = models.CharField(
        max_length=200,
        validators=[
            MinLengthValidator(1, message="عنوان تسک نمی‌تواند خالی باشد"),
            MaxLengthValidator(200, message="عنوان تسک نمی‌تواند بیشتر از 200 کاراکتر باشد")
        ],
        verbose_name="عنوان",
        db_index=True  # ✅ ایندکس اضافه شد
    )
    description = models.TextField(
        blank=True,
        null=True,
        validators=[
            MaxLengthValidator(1000, message="توضیحات نمی‌تواند بیشتر از 1000 کاراکتر باشد")
        ],
        verbose_name="توضیحات"
    )
    completed = models.BooleanField(default=False, verbose_name="انجام شده", db_index=True)  # ✅ ایندکس اضافه شد
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد", db_index=True)  # ✅ ایندکس اضافه شد
    due_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="تاریخ ددلاین",
        db_index=True  # ✅ ایندکس اضافه شد
    )
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        verbose_name = 'تسک'
        verbose_name_plural = 'تسک‌ها'
        indexes = [
            models.Index(fields=['user', '-created_at']),  # ✅ ایندکس ترکیبی اضافه شد
            models.Index(fields=['completed', '-due_date']),  # ✅ ایندکس ترکیبی اضافه شد
        ]
    
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        """بررسی اینکه آیا تسک از تاریخ ددلاین عقب افتاده است"""
        from datetime import date
        if self.due_date and not self.completed:
            return self.due_date < date.today()
        return False
    
    def get_status_display(self):
        """نمایش وضعیت تسک به صورت متنی"""
        if self.completed:
            return "انجام شده"
        elif self.is_overdue():
            return "عقب افتاده"
        else:
            return "در حال انجام"