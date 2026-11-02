from django.contrib import admin
from .models import User, Task


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'created_at', 'get_task_count']
    search_fields = ['username']
    readonly_fields = ['created_at']
    
    def get_task_count(self, obj):
        return obj.get_task_count()
    get_task_count.short_description = 'تعداد تسک‌ها'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'completed', 'due_date', 'created_at', 'get_status_display']
    list_filter = ['completed', 'created_at', 'due_date', 'user']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'title', 'description')
        }),
        ('وضعیت', {
            'fields': ('completed',)
        }),
        ('تاریخ', {
            'fields': ('due_date', 'created_at')
        }),
    )