class FormValidator {
    // اعتبارسنجی یوزرنیم
    static validateUsername(username) {
        const errors = [];
        
        if (!username || username.trim() === '') {
            errors.push('نام کاربری نمی‌تواند خالی باشد');
        }
        
        if (username && username.length < 3) {
            errors.push('نام کاربری باید حداقل 3 کاراکتر باشد');
        }
        
        if (username && username.length > 50) {
            errors.push('نام کاربری نمی‌تواند بیشتر از 50 کاراکتر باشد');
        }
        
        if (username && !/^[a-zA-Z][a-zA-Z0-9_]*$/.test(username)) {
            errors.push('نام کاربری فقط می‌تواند شامل حروف، اعداد و آندرلاین باشد و نباید با عدد شروع شود');
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
    
    // اعتبارسنجی عنوان تسک
    static validateTaskTitle(title) {
        const errors = [];
        
        if (!title || title.trim() === '') {
            errors.push('عنوان تسک نمی‌تواند خالی باشد');
        }
        
        if (title && title.length > 200) {
            errors.push('عنوان تسک نمی‌تواند بیشتر از 200 کاراکتر باشد');
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
    
    // اعتبارسنجی توضیحات
    static validateDescription(description) {
        const errors = [];
        
        if (description && description.length > 1000) {
            errors.push('توضیحات نمی‌تواند بیشتر از 1000 کاراکتر باشد');
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
    
    // اعتبارسنجی تاریخ
    static validateDueDate(dateStr) {
        const errors = [];
        
        if (dateStr) {
            const inputDate = new Date(dateStr);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (inputDate < today) {
                errors.push('تاریخ ددلاین نمی‌تواند از تاریخ امروز کوچکتر باشد');
            }
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
    
    // اعتبارسنجی کامل فرم تسک
    static validateTaskForm(title, description, dueDate) {
        const errors = [];
        
        const titleValidation = this.validateTaskTitle(title);
        const descValidation = this.validateDescription(description);
        const dateValidation = this.validateDueDate(dueDate);
        
        errors.push(...titleValidation.errors);
        errors.push(...descValidation.errors);
        errors.push(...dateValidation.errors);
        
        return {
            valid: titleValidation.valid && descValidation.valid && dateValidation.valid,
            errors: errors
        };
    }
    
    // نمایش خطاها
    static showError(elementId, errors) {
        const errorElement = document.getElementById(elementId);
        if (!errorElement) return;
        
        if (errors.length > 0) {
            errorElement.textContent = errors.join('\n');
            errorElement.classList.add('show');
        } else {
            errorElement.classList.remove('show');
        }
    }
    
    // پاک کردن خطاها
    static clearError(elementId) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.classList.remove('show');
            errorElement.textContent = '';
        }
    }
}