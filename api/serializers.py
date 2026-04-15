from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Statue, SearchHistory

# 1. Serializer للمستخدم (للتسجيل واللوجن)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}} # الباسورد يتبعت بس مش بيرجع في الـ JSON للأمان

    def create(self, validated_data):
        # تشفير الباسورد قبل الحفظ في الداتابيز
        user = User.objects.create_user(**validated_data)
        return user

# 2. Serializer لبيانات التماثيل
class StatueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statue
        fields = '__all__' # هيبعت كل الخانات (الاسم، العصر، الوصف، إلخ)

# 3. Serializer لسجل البحث (History)
class SearchHistorySerializer(serializers.ModelSerializer):
    # هنا بنقول للديجانجو يرجع بيانات التمثال كاملة جوه الهيستوري مش مجرد الـ ID بتاعه
    statue_details = StatueSerializer(source='statue', read_only=True)
    
    class Meta:
        model = SearchHistory
        fields = ['id', 'statue', 'statue_details', 'image_searched', 'confidence', 'created_at']