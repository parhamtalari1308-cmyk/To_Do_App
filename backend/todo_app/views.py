from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from .models import User, Task
from .validators import (
    validate_username, 
    validate_task_data, 
    validate_task_title,        
    validate_task_description,  
    validate_due_date,           
    validate_user_exists,
    sanitize_input
)
from .serializers import (
    serialize_user,
    serialize_task,
    serialize_users,
    serialize_tasks,
    deserialize_date,
    format_response
)
import json


# ============================================
# User Endpoints
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
def set_user(request):
    """
    انتخاب یا ایجاد کاربر
    POST /api/set-user/
    Body: {"username": "ali"}
    """
    try:
        # Parse JSON
        data = json.loads(request.body)
        username = sanitize_input(data.get('username', '').strip())
        
        # Validate username
        try:
            validate_username(username)
        except ValidationError as e:
            return JsonResponse(
                format_response(
                    success=False,
                    message=str(e),
                    errors={'username': str(e)}
                ),
                status=400
            )
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
            message = "کاربر انتخاب شد"
            created = False
        except User.DoesNotExist:
            # Create new user
            user = User(username=username)
            user.save()
            message = "کاربر جدید ایجاد شد"
            created = True
        
        return JsonResponse(
            format_response(
                success=True,
                message=message,
                data={
                    'user': serialize_user(user),
                    'created': created
                }
            )
        )
    
    except json.JSONDecodeError:
        return JsonResponse(
            format_response(
                success=False,
                message="داده‌های ورودی معتبر نیستند",
                errors={'body': 'Invalid JSON'}
            ),
            status=400
        )
    except Exception as e:
        return JsonResponse(
            format_response(
                success=False,
                message=f"خطای سرور: {str(e)}",
                errors={'server': str(e)}
            ),
            status=500
        )


@require_http_methods(["GET"])
def get_users(request):
    """
    لیست تمام کاربران - با بهینه‌سازی
    GET /api/users/
    """
    try:
        # استفاده از prefetch_related برای کاهش تعداد کوئری‌ها
        users = User.objects.all().prefetch_related('tasks')
        return JsonResponse(
            format_response(
                success=True,
                data={
                    'users': serialize_users(users),
                    'count': users.count()
                }
            )
        )
    except Exception as e:
        return JsonResponse(
            format_response(
                success=False,
                message=f"خطای سرور: {str(e)}"
            ),
            status=500
        )

# ============================================
# Task Endpoints
# ============================================

@require_http_methods(["GET"])
def get_tasks(request):
    """
    لیست تسک‌های کاربر - با بهینه‌سازی
    GET /api/tasks/?user_id=1
    """
    try:
        user_id = request.GET.get('user_id')
        
        if not user_id:
            return JsonResponse(
                format_response(
                    success=False,
                    message="شناسه کاربر الزامی است",
                    errors={'user_id': 'Required'}
                ),
                status=400
            )
        
        # Validate user exists
        try:
            user = validate_user_exists(int(user_id))
        except ValidationError as e:
            return JsonResponse(
                format_response(
                    success=False,
                    message=str(e),
                    errors={'user_id': str(e)}
                ),
                status=404
            )
        except ValueError:
            return JsonResponse(
                format_response(
                    success=False,
                    message="شناسه کاربر معتبر نیست",
                    errors={'user_id': 'Invalid ID'}
                ),
                status=400
            )
        
        # Get tasks for user - با استفاده از select_related برای کاهش کوئری‌ها
        tasks = Task.objects.filter(user=user).select_related('user').order_by('-created_at')
        
        return JsonResponse(
            format_response(
                success=True,
                data={
                    'tasks': serialize_tasks(tasks),
                    'count': tasks.count(),
                    'user': serialize_user(user)
                }
            )
        )
    
    except Exception as e:
        return JsonResponse(
            format_response(
                success=False,
                message=f"خطای سرور: {str(e)}"
            ),
            status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def create_task(request):
    """
    ایجاد تسک جدید
    POST /api/tasks/create/
    Body: {
        "user_id": 1,
        "title": "تسک جدید",
        "description": "توضیحات",
        "due_date": "2026-02-10"
    }
    """
    try:
        data = json.loads(request.body)
        
        # Validate user_id
        user_id = data.get('user_id')
        if not user_id:
            return JsonResponse(
                format_response(
                    success=False,
                    message="شناسه کاربر الزامی است",
                    errors={'user_id': 'Required'}
                ),
                status=400
            )
        
        try:
            user = validate_user_exists(int(user_id))
        except ValidationError as e:
            return JsonResponse(
                format_response(
                    success=False,
                    message=str(e),
                    errors={'user_id': str(e)}
                ),
                status=404
            )
        
        # Sanitize inputs
        title = sanitize_input(data.get('title', '').strip())
        description = sanitize_input(data.get('description', '').strip())
        due_date_str = data.get('due_date')
        due_date = deserialize_date(due_date_str) if due_date_str else None
        
        # Validate task data
        validation_errors = validate_task_data({
            'title': title,
            'description': description,
            'due_date': due_date
        })
        
        if validation_errors:
            return JsonResponse(
                format_response(
                    success=False,
                    message="داده‌های نامعتبر",
                    errors=validation_errors
                ),
                status=400
            )
        
        # Create task
        task = Task(
            user=user,
            title=title,
            description=description or None,
            due_date=due_date
        )
        task.save()
        
        return JsonResponse(
            format_response(
                success=True,
                message="تسک با موفقیت ایجاد شد",
                data={'task': serialize_task(task)}
            ),
            status=201
        )
    
    except json.JSONDecodeError:
        return JsonResponse(
            format_response(
                success=False,
                message="داده‌های ورودی معتبر نیستند",
                errors={'body': 'Invalid JSON'}
            ),
            status=400
        )
    except Exception as e:
        return JsonResponse(
            format_response(
                success=False,
                message=f"خطای سرور: {str(e)}",
                errors={'server': str(e)}
            ),
            status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def update_task(request, task_id):
    """
    ویرایش تسک
    POST /api/tasks/<id>/update/
    Body: {
        "title": "عنوان جدید",
        "description": "توضیحات جدید",
        "due_date": "2026-02-15",
        "completed": false
    }
    """
    try:
        # Get task
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse(
                format_response(
                    success=False,
                    message="تسک یافت نشد",
                    errors={'task_id': 'Not found'}
                ),
                status=404
            )
        
        # Parse data
        data = json.loads(request.body)
        
        # Update fields if provided
        if 'title' in data and data['title'] is not None:
            title = sanitize_input(str(data['title']).strip())
            try:
                validate_task_title(title)
                task.title = title
            except ValidationError as e:
                return JsonResponse(
                    format_response(
                        success=False,
                        message=str(e),
                        errors={'title': str(e)}
                    ),
                    status=400
                )
        
        if 'description' in data and data['description'] is not None:
            description = sanitize_input(str(data['description']).strip())
            try:
                validate_task_description(description)
                task.description = description or None
            except ValidationError as e:
                return JsonResponse(
                    format_response(
                        success=False,
                        message=str(e),
                        errors={'description': str(e)}
                    ),
                    status=400
                )
        
        if 'due_date' in data:
            due_date = deserialize_date(data['due_date'])
            try:
                if due_date:
                    validate_due_date(due_date)
                task.due_date = due_date
            except ValidationError as e:
                return JsonResponse(
                    format_response(
                        success=False,
                        message=str(e),
                        errors={'due_date': str(e)}
                    ),
                    status=400
                )
        
        if 'completed' in data:
            task.completed = bool(data['completed'])
        
        # Save task
        task.save()
        
        return JsonResponse(
            format_response(
                success=True,
                message="تسک با موفقیت ویرایش شد",
                data={'task': serialize_task(task)}
            )
        )
    
    except json.JSONDecodeError:
        return JsonResponse(
            format_response(
                success=False,
                message="داده‌های ورودی معتبر نیستند",
                errors={'body': 'Invalid JSON'}
            ),
            status=400
        )
    except Exception as e:
        return JsonResponse(
            format_response(
                success=False,
                message=f"خطای سرور: {str(e)}",
                errors={'server': str(e)}
            ),
            status=500
        )

@csrf_exempt
@require_http_methods(["POST"])
def toggle_complete(request, task_id):
    """
    تغییر وضعیت انجام تسک
    POST /api/tasks/<id>/toggle-complete/
    """
    try:
        # Get task
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse(
                format_response(
                    success=False,
                    message="تسک یافت نشد",
                    errors={'task_id': 'Not found'}
                ),
                status=404
            )
        
        # Toggle completed status
        task.completed = not task.completed
        task.save()
        
        status_text = "انجام شده" if task.completed else "در حال انجام"
        
        return JsonResponse(
            format_response(
                success=True,
                message=f"وضعیت تسک به '{status_text}' تغییر کرد",
                data={
                    'task': serialize_task(task),
                    'completed': task.completed
                }
            )
        )
    
    except Exception as e:
        return JsonResponse(
            format_response(
                success=False,
                message=f"خطای سرور: {str(e)}",
                errors={'server': str(e)}
            ),
            status=500
        )


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    """
    حذف تسک
    DELETE /api/tasks/<id>/delete/
    """
    try:
        # Get task
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse(
                format_response(
                    success=False,
                    message="تسک یافت نشد",
                    errors={'task_id': 'Not found'}
                ),
                status=404
            )
        
        # Save task info before deletion
        task_info = serialize_task(task)
        
        # Delete task
        task.delete()
        
        return JsonResponse(
            format_response(
                success=True,
                message="تسک با موفقیت حذف شد",
                data={'task': task_info}
            )
        )
    
    except Exception as e:
        return JsonResponse(
            format_response(
                success=False,
                message=f"خطای سرور: {str(e)}",
                errors={'server': str(e)}
            ),
            status=500
        )