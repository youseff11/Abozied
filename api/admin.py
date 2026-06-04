from django.contrib import admin
from django.utils.html import format_html
from .models import Statue, SearchHistory

# ─── 1. تخصيص عرض جدول التماثيل ───
@admin.register(Statue)
class StatueAdmin(admin.ModelAdmin):
    # الخانات اللي هتظهر في الجدول بره (أضفنا دالة عرض الصورة)
    list_display = ('label_ar', 'name', 'era', 'museum', 'display_statue_image')
    # خانات البحث
    search_fields = ('label_ar', 'name')
    # فلاتر جانبية
    list_filter = ('era', 'museum')
    # عشان الصورة تظهر جوه صفحة التعديل (زي اللي في الصورة عندك) للقراءة فقط
    readonly_fields = ('display_statue_image',)

    # دالة عرض الصورة المرجعية للتمثال
    def display_statue_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 80px; height: auto; border-radius: 8px; border: 1px solid #ddd;" />', obj.image.url)
        return "لا توجد صورة مرجعية"
    
    display_statue_image.short_description = 'معاينة الصورة المرجعية'


# ─── 2. تخصيص عرض سجل البحث ───
@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    # الخانات اللي هتظهر في الجدول بره
    list_display = ('user', 'get_statue_name', 'confidence', 'display_searched_image', 'created_at')
    # فلاتر جانبية
    list_filter = ('created_at', 'user')
    # جعل الخانات للقراءة فقط
    readonly_fields = ('created_at', 'display_searched_image')

    # دالة لعرض اسم التمثال
    def get_statue_name(self, obj):
        return obj.statue.label_ar if obj.statue else "Unknown"
    get_statue_name.short_description = 'التمثال الذي تم التعرف عليه'

    # دالة عرض الصورة التي رفعها المستخدم أثناء البحث
    def display_searched_image(self, obj):
        if obj.image_searched:
            return format_html('<img src="{}" style="width: 60px; height: auto; border-radius: 8px; border: 1px solid #ddd;" />', obj.image_searched.url)
        return "لا توجد صورة"
    
    display_searched_image.short_description = 'الصورة المرفوعة'