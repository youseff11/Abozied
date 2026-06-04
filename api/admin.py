from django.contrib import admin
from django.utils.html import format_html # ✅ استيراد أداة عرض الـ HTML الآمن
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
    # ✅ تم إضافة 'display_searched_image' هنا لتعرض الصورة في الجدول بره
    list_display = ('user', 'get_statue_name', 'confidence', 'display_searched_image', 'created_at')
    
    # فلتر عشان تشوف عمليات البحث اللي حصلت في يوم معين أو ليوزر معين
    list_filter = ('created_at', 'user')
    
    # ✅ جعل الصورة والوقت للقراءة فقط عشان الأمان وم تضربش كراش داخل لوحة التحكم
    readonly_fields = ('created_at', 'display_searched_image')

    # دالة بسيطة لعرض اسم التمثال في الجدول
    def get_statue_name(self, obj):
        return obj.statue.label_ar if obj.statue else "Unknown"
    get_statue_name.short_description = 'التمثال الذي تم التعرف عليه'

    # ✅ الدالة السحرية لعرض الصورة المرفوعة بشكل مصغر واحترافي
    def display_searched_image(self, obj):
        if obj.image_searched:
            # بنعرض الصورة بعرض 60 بكسل وبحواف دائرية ناعمة تليق بـ Clean UI
            return format_html('<img src="{}" style="width: 60px; height: auto; border-radius: 8px; border: 1px solid #ddd;" />', obj.image_searched.url)
        return "لا توجد صورة"
    
    # الاسم اللي هيظهر فوق في رأس الجدول بالـ Admin
    display_searched_image.short_description = 'الصورة المرفوعة'