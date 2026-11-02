class Utils {
    // نمایش پیام موفقیت
    static showSuccess(message, duration = 3000) {
        alert('✅ ' + message);
    }
    
    // نمایش پیام خطا
    static showError(message) {
        alert('❌ ' + message);
    }
    
    // نمایش پیام اطلاع
    static showInfo(message) {
        alert('ℹ️ ' + message);
    }
    
    // تبدیل تاریخ به فرمت فارسی
    static formatDate(dateString) {
        if (!dateString) return '-';
        
        const date = new Date(dateString);
        return date.toLocaleDateString('fa-IR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
    
    // تبدیل تاریخ به فرمت قابل نمایش
    static formatDateTime(dateString) {
        if (!dateString) return '-';
        
        const date = new Date(dateString);
        return date.toLocaleString('fa-IR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    // بررسی تاریخ گذشته
    static isOverdue(dateString) {
        if (!dateString) return false;
        
        const dueDate = new Date(dateString);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        dueDate.setHours(0, 0, 0, 0);
        
        return dueDate < today;
    }
    
    // ذخیره در localStorage
    static saveToLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Error saving to localStorage:', e);
            return false;
        }
    }
    
    // دریافت از localStorage
    static getFromLocalStorage(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.error('Error getting from localStorage:', e);
            return null;
        }
    }
    
    // حذف از localStorage
    static removeFromLocalStorage(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('Error removing from localStorage:', e);
            return false;
        }
    }
    
    // کپی متن به کلیپ‌بورد
    static copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showSuccess('متن کپی شد!');
        }).catch(err => {
            this.showError('خطا در کپی متن');
            console.error('Could not copy text: ', err);
        });
    }
    
    // تبدیل متن به اسلاگ
    static slugify(text) {
        return text.toString().toLowerCase()
            .replace(/\s+/g, '-')
            .replace(/[^\w\-]+/g, '')
            .replace(/\-\-+/g, '-')
            .replace(/^-+/, '')
            .replace(/-+$/, '');
    }
    
    // ایجاد اعلان
    static notify(message, type = 'info') {
        // می‌توان اینجا یک سیستم نوتیفیکیشن زیبا اضافه کرد
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}