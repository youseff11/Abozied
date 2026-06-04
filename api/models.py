from django.db import models
from django.contrib.auth.models import User

# 1. موديل التماثيل
class Statue(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم التمثال (انجليزي كما يظهر من الموديل)")
    label_ar = models.CharField(max_length=100, verbose_name="الاسم بالعربي")
    era = models.CharField(max_length=100, verbose_name="العصر")
    museum = models.CharField(max_length=200, verbose_name="المتحف الموجود به")
    description = models.TextField(verbose_name="وصف تفصيلي للتمثال")
    image = models.ImageField(upload_to='statues_db/', blank=True, null=True, verbose_name="صورة مرجعية")

    def __str__(self):
        return self.label_ar

# 2. موديل سجل عمليات البحث
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    statue = models.ForeignKey(Statue, on_delete=models.SET_NULL, null=True, blank=True)
    image_searched = models.ImageField(upload_to='user_searches/', verbose_name="الصورة التي رفعها المستخدم")
    confidence = models.FloatField(verbose_name="نسبة التأكد")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت البحث")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.statue.label_ar if self.statue else 'Unknown'}"

# 3. موديل معالم مصر (الجديد)
class Landmark(models.Model):
    title_ar = models.CharField(max_length=200, verbose_name="العنوان بالعربي")
    title_en = models.CharField(max_length=200, verbose_name="العنوان بالانجليزي")
    desc_ar = models.TextField(verbose_name="الوصف بالعربي")
    desc_en = models.TextField(verbose_name="الوصف بالانجليزي")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title_ar

# 4. موديل صور المعالم (عشان نقبل أكتر من صورة للمعلم الواحد)
class LandmarkImage(models.Model):
    landmark = models.ForeignKey(Landmark, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='landmarks/', verbose_name="الصورة")

    def __str__(self):
        return f"صورة تابعة لـ: {self.landmark.title_ar}"