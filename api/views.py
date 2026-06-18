import requests
import logging
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Statue, SearchHistory, Landmark
from .serializers import StatueSerializer, UserSerializer, SearchHistorySerializer, LandmarkSerializer

logger = logging.getLogger(__name__)

# الرابط الفعلي للـ AI Model 
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


# --- 3. التنبؤ بالتمثال (بالهيكل الجديد المخصص للـ JSON) ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def predict_artifact(request):
    if 'image' not in request.FILES:
        return Response({
            "prediction_type": "not_statue",
            "confidence": 0.0,
            "statue_info": None,
            "era_info": None,
            "closest_match": None,
            "message": "لم يتم استلام صورة."
        }, status=400)

    try:
        image_file = request.FILES['image']
        
        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type)
        }

        # إرسال طلب الـ POST لخادم الـ AI
        response = requests.post(AI_MODEL_URL, files=files, timeout=25)

        if response.status_code == 200:
            res = response.json()
            
            # استخراج البيانات الأساسية من رد الـ AI
            prediction_type = res.get('prediction_type', 'unknown')
            confidence = res.get('confidence', 0.0)
            
            ai_statue_info = res.get('statue_info') or {}
            label_name = ai_statue_info.get('name_en')

            # ── [الحالة الأولى]: الـ AI حدد تمثال بنجاح ──
            if prediction_type == "statue" and label_name:
                try:
                    statue_obj = Statue.objects.get(name=label_name)

                    # حفظ العملية في سجل البحث للمستخدم
                    image_file.seek(0)
                    SearchHistory.objects.create(
                        user=request.user,
                        statue=statue_obj,
                        image_searched=image_file,
                        confidence=confidence * 100 if confidence <= 1.0 else confidence
                    )

                    # إرجاع الجيسون بالهيكل المطلوب بالظبط مع دمج بيانات الداتا بيز المحلية والـ AI
                    return Response({
                        "prediction_type": "statue",
                        "confidence": confidence,
                        "statue_info": {
                            "name_ar": statue_obj.label_ar,
                            "name_en": statue_obj.name,
                            "era_ar": statue_obj.era,
                            "era_en": ai_statue_info.get('era_en', ''),
                            "dynasty_ar": ai_statue_info.get('dynasty_ar', ''),
                            "dynasty_en": ai_statue_info.get('dynasty_en', ''),
                            "description_ar": statue_obj.description,
                            "description_en": ai_statue_info.get('description_en', ''),
                            "museum": statue_obj.museum,
                            "local_image": request.build_absolute_uri(statue_obj.image.url) if statue_obj.image else None
                        },
                        "era_info": None,
                        "closest_match": None
                    }, status=200)

                except Statue.DoesNotExist:
                    # في حال التعرف عليه لكنه مش متسجل في الداتا بيز المحلية
                    return Response({
                        "prediction_type": "statue",
                        "confidence": confidence,
                        "statue_info": ai_statue_info,
                        "era_info": None,
                        "closest_match": None,
                        "message": f"التمثال '{label_name}' تم التعرف عليه ولكن غير مسجل محلياً."
                    }, status=200)

            # ── [الحالة الثانية]: الموديل حدد "عصر تاريخي عام" ──
            elif prediction_type == "era":
                image_file.seek(0)
                SearchHistory.objects.create(
                    user=request.user,
                    statue=None,
                    image_searched=image_file,
                    confidence=confidence * 100 if confidence <= 1.0 else confidence
                )

                return Response({
                    "prediction_type": "era",
                    "confidence": confidence,
                    "statue_info": None,
                    "era_info": res.get('era_info'),
                    "closest_match": res.get('closest_match')
                }, status=200)

            # ── [الحالة الثالثة]: الصورة ليست تمثالاً أثرياً ──
            else:
                return Response({
                    "prediction_type": "not_statue",
                    "confidence": confidence,
                    "statue_info": None,
                    "era_info": None,
                    "closest_match": None,
                    "message": "عذراً، لم يتم التعرف على تمثال أثري في هذه الصورة."
                }, status=200)

        return Response({
            "prediction_type": "error",
            "confidence": 0.0,
            "statue_info": None,
            "era_info": None,
            "closest_match": None,
            "message": f"خطأ من خادم الـ AI الخارجي: {response.status_code}"
        }, status=500)

    except requests.exceptions.Timeout:
        return Response({
            "prediction_type": "error",
            "confidence": 0.0,
            "statue_info": None,
            "era_info": None,
            "closest_match": None,
            "message": "انتهت مهلة الاتصال بخادم الـ AI الخارجي."
        }, status=504)
    except Exception as e:
        logger.error(f"predict_artifact error: {e}")
        return Response({
            "prediction_type": "error",
            "confidence": 0.0,
            "statue_info": None,
            "era_info": None,
            "closest_match": None,
            "message": f"خطأ داخلي: {str(e)}"
        }, status=500)


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

# --- 6. جلب المعالم المصرية ---
@api_view(['GET'])
@permission_classes([IsAuthenticated]) # أو AllowAny لو عايزها تظهر للزوار
def get_landmarks(request):
    landmarks = Landmark.objects.all()
    serializer = LandmarkSerializer(landmarks, many=True, context={'request': request})
    return Response({
        "success": True,
        "landmarks": serializer.data
    }, status=200)