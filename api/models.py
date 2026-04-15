from django.db import models
from django.contrib.auth.models import User

# 1. موديل التماثيل (عشان تخزن معلومات الـ 8 تماثيل بتوعك)
class Statue(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم التمثال (انجليزي كما يظهر من الموديل)")
    label_ar = models.CharField(max_length=100, verbose_name="الاسم بالعربي")
    era = models.CharField(max_length=100, verbose_name="العصر")
    museum = models.CharField(max_length=200, verbose_name="المتحف الموجود به")
    description = models.TextField(verbose_name="وصف تفصيلي للتمثال")
    image = models.ImageField(upload_to='statues_db/', blank=True, null=True, verbose_name="صورة مرجعية")

    def __str__(self):
        return self.label_ar

# 2. موديل سجل عمليات البحث (Search History)
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    statue = models.ForeignKey(Statue, on_delete=models.SET_NULL, null=True, blank=True)
    image_searched = models.ImageField(upload_to='user_searches/', verbose_name="الصورة التي رفعها المستخدم")
    confidence = models.FloatField(verbose_name="نسبة التأكد")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت البحث")

    class Meta:
        ordering = ['-created_at'] # عشان يظهر الأحدث الأول في Flutter

    def __str__(self):
        return f"{self.user.username} - {self.statue.label_ar if self.statue else 'Unknown'}"