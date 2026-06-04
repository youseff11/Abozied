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

@admin.register(Landmark)
class LandmarkAdmin(admin.ModelAdmin):
    list_display = ('title_ar', 'title_en', 'created_at')
    search_fields = ('title_ar', 'title_en')
    inlines = [LandmarkImageInline] 