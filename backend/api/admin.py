from django.contrib import admin
from .models import Statue, SearchHistory

# تخصيص عرض جدول التماثيل في لوحة التحكم
@admin.register(Statue)
class StatueAdmin(admin.ModelAdmin):
    # الخانات اللي هتظهر في الجدول بره
    list_display = ('label_ar', 'name', 'era', 'museum')
    # خانات البحث (تقدر تبحث بالاسم العربي أو الإنجليزي)
    search_fields = ('label_ar', 'name')
    # فلاتر جانبية
    list_filter = ('era', 'museum')

# تخصيص عرض سجل البحث
@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_statue_name', 'confidence', 'created_at')
    # فلتر عشان تشوف عمليات البحث اللي حصلت في يوم معين أو ليوزر معين
    list_filter = ('created_at', 'user')
    # لمنع التعديل في السجل (يكون للقراءة فقط عشان الأمان)
    readonly_fields = ('created_at',)

    # دالة بسيطة لعرض اسم التمثال في الجدول
    def get_statue_name(self, obj):
        return obj.statue.label_ar if obj.statue else "Unknown"
    get_statue_name.short_description = 'التمثال الذي تم التعرف عليه'