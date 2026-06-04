from django.contrib import admin
from django.utils.html import format_html
from .models import Statue, SearchHistory, Landmark, LandmarkImage

@admin.register(Statue)
class StatueAdmin(admin.ModelAdmin):
    list_display = ('label_ar', 'name', 'era', 'museum', 'display_statue_image')
    search_fields = ('label_ar', 'name')
    list_filter = ('era', 'museum')
    readonly_fields = ('display_statue_image',)

    def display_statue_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 80px; height: auto; border-radius: 8px; border: 1px solid #ddd;" />', obj.image.url)
        return "لا توجد صورة مرجعية"
    display_statue_image.short_description = 'معاينة الصورة المرجعية'


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_statue_name', 'confidence', 'display_searched_image', 'created_at')
    list_filter = ('created_at', 'user')
    readonly_fields = ('created_at', 'display_searched_image')

    def get_statue_name(self, obj):
        return obj.statue.label_ar if obj.statue else "Unknown"
    get_statue_name.short_description = 'التمثال الذي تم التعرف عليه'

    def display_searched_image(self, obj):
        if obj.image_searched:
            return format_html('<img src="{}" style="width: 60px; height: auto; border-radius: 8px; border: 1px solid #ddd;" />', obj.image_searched.url)
        return "لا توجد صورة"
    display_searched_image.short_description = 'الصورة المرفوعة'


# --- إعدادات المعالم الجديدة والصور المتعددة ---

class LandmarkImageInline(admin.TabularInline):
    model = LandmarkImage
    extra = 1 # بيفتحلك خانة فاضية دايماً لرفع صورة جديدة
    readonly_fields = ('display_image_preview',) # لعرض الصورة المرفوعة داخل صفحة المعلم

    def display_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 80px; height: auto; border-radius: 8px; border: 1px solid #ddd;" />', obj.image.url)
        return "لا توجد صورة"
    display_image_preview.short_description = 'معاينة الصورة'


@admin.register(Landmark)
class LandmarkAdmin(admin.ModelAdmin):
    # إضافة صورة العرض الرئيسية في الجدول الخارجي
    list_display = ('title_ar', 'title_en', 'display_first_image', 'created_at')
    search_fields = ('title_ar', 'title_en')
    inlines = [LandmarkImageInline]

    def display_first_image(self, obj):
        # جلب أول صورة مرتبطة بهذا المعلم لعرضها في الجدول
        first_image = obj.images.first() 
        if first_image and first_image.image:
            return format_html('<img src="{}" style="width: 60px; height: auto; border-radius: 8px; border: 1px solid #ddd;" />', first_image.image.url)
        return "لا توجد صورة"
    display_first_image.short_description = 'صورة العرض'