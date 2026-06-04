import requests
import logging
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Statue, SearchHistory
from .serializers import StatueSerializer, UserSerializer, SearchHistorySerializer
from .models import Landmark
from .serializers import LandmarkSerializer
logger = logging.getLogger(__name__)

# الرابط الفعلي للـ AI Model بناءً على توثيق الـ Swagger الخاص بك
AI_MODEL_URL = "https://hamodyyy1-statue-recognition-api.hf.space/api/v1/predict"


# --- 1. تسجيل مستخدم جديد ---
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "success": True,
            "token": token.key,
            "username": user.username
        }, status=201)
    return Response(serializer.errors, status=400)


# --- 2. تسجيل الدخول ---
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    from django.contrib.auth import authenticate
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "success": True,
            "token": token.key,
            "username": user.username
        }, status=200)
    return Response({"success": False, "message": "Invalid Credentials"}, status=401)


# --- 3. التنبؤ بالتمثال (باستخدام نموذج FastAPI الجديد والمؤمن بالكامل) + حفظ في السجل ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def predict_artifact(request):
    if 'image' not in request.FILES:
        return Response({"success": False, "message": "لم يتم استلام صورة."}, status=400)

    try:
        image_file = request.FILES['image']
        
        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type)
        }

        # إرسال طلب الـ POST لخادم الـ AI
        response = requests.post(AI_MODEL_URL, files=files, timeout=25)

        if response.status_code == 200:
            res = response.json()
            
            # ✅ تأمين معالجة الـ statue_info حتى لو عادت قيمتها null صريحة من السيرفر الخارجي
            statue_info = res.get('statue_info')
            if not statue_info:
                statue_info = {}
                
            label_name = statue_info.get('name_en')
            
            confidence = res.get('confidence', 0)
            if confidence <= 1.0:
                confidence = confidence * 100

            prediction_type = res.get('prediction_type', 'unknown')

            # ── [الحالة الأولى]: الـ AI حدد تمثال مبرمج بنجاح ──
            if prediction_type == "statue" and label_name:
                try:
                    statue_obj = Statue.objects.get(name=label_name)
                    statue_data = StatueSerializer(statue_obj).data

                    # حفظ العملية في سجل البحث للمستخدم
                    image_file.seek(0)
                    SearchHistory.objects.create(
                        user=request.user,
                        statue=statue_obj,
                        image_searched=image_file,
                        confidence=confidence
                    )

                    return Response({
                        "success": True,
                        "label": label_name,
                        "confidence": round(confidence, 1),
                        "data": statue_data
                    }, status=200)

                except Statue.DoesNotExist:
                    return Response({
                        "success": False,
                        "message": f"التمثال '{label_name}' تم التعرف عليه ولكن غير مسجل في قاعدة البيانات المحلية."
                    }, status=200)

            # ── [الحالة الثانية]: الموديل لم يحدد تمثالاً بل حدد "عصر تاريخي عام" (Era Fallback) ──
            elif prediction_type == "era":
                era_info = res.get('era_info', {}) or {}
                era_name_ar = era_info.get('name_ar', 'غير معروف')
                closest = res.get('closest_match', {}) or {}
                closest_name = closest.get('name', 'غير محدد')

                # بناء هيكل بيانات مرن يتناسب مع الـ ResultScreen في الفلاتر لمنع أي Crash أونلاين
                fallback_data = {
                    "label_ar": f"عصر: {era_name_ar}",
                    "era": era_name_ar,
                    "museum": "بحاجة لفحص أدق",
                    "description": f"لم يستطع الـ AI تحديد التمثال بدقة 100%، ولكن بتحليل الخصائص الفنية تبيّن أن القطعة تنتمي إلى ({era_name_ar}).\n\nأقرب تمثال متوقع لهذه البنية المعمارية هو: {closest_name}."
                }

                return Response({
                    "success": True,
                    "label": closest_name,
                    "confidence": round(confidence, 1),
                    "data": fallback_data
                }, status=200)

            # ── [الحالة الثالثة]: الصورة ليست تمثالاً أثرياً من الأساس (not_statue) ──
            else:
                return Response({
                    "success": False,
                    "message": "عذراً، لم يتم التعرف على تمثال أثري في هذه الصورة."
                }, status=200)

        return Response({
            "success": False, 
            "message": f"خطأ من خادم الـ AI الخارجي: {response.status_code}"
        }, status=500)

    except requests.exceptions.Timeout:
        return Response({"success": False, "message": "انتهت مهلة الاتصال بخادم الـ AI الخارجي."}, status=504)
    except Exception as e:
        logger.error(f"predict_artifact error: {e}")
        return Response({"success": False, "message": f"خطأ داخلي: {str(e)}"}, status=500)


# --- 4. جلب سجل البحث للمستخدم ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_search_history(request):
    history = SearchHistory.objects.filter(user=request.user).select_related('statue')[:20]
    serializer = SearchHistorySerializer(history, many=True, context={'request': request})
    return Response({
        "success": True,
        "history": serializer.data
    }, status=200)


# --- 5. بيانات المستخدم الحالي ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    history_count = SearchHistory.objects.filter(user=user).count()
    return Response({
        "success": True,
        "username": user.username,
        "email": user.email,
        "history_count": history_count,
        "date_joined": user.date_joined.strftime("%Y-%m-%d"),
    }, status=200)

# جلب المعالم المصريه
@api_view(['GET'])
@permission_classes([IsAuthenticated]) # أو AllowAny لو عايزها تظهر للزوار
def get_landmarks(request):
    landmarks = Landmark.objects.all()
    serializer = LandmarkSerializer(landmarks, many=True, context={'request': request})
    return Response({
        "success": True,
        "landmarks": serializer.data
    }, status=200)