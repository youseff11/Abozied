import requests
import base64
import logging
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Statue, SearchHistory
from .serializers import StatueSerializer, UserSerializer, SearchHistorySerializer

logger = logging.getLogger(__name__)

ROBOFLOW_API_KEY = "0Q95f8rFPiohq2RfJuR9"
MODEL_ID = "egyptian-statues/4"


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


# --- 3. التنبؤ بالتمثال + حفظ في السجل ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def predict_artifact(request):
    if 'image' not in request.FILES:
        return Response({"success": False, "message": "لم يتم استلام صورة."}, status=400)

    try:
        image_file = request.FILES['image']
        image_bytes = image_file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        rf_url = f"https://classify.roboflow.com/{MODEL_ID}?api_key={ROBOFLOW_API_KEY}"
        response = requests.post(
            rf_url,
            data=image_base64,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15
        )

        if response.status_code == 200:
            res = response.json()
            predictions = res.get('predictions', [])

            if predictions:
                top = predictions[0]
                label_name = top['class']
                confidence = top['confidence'] * 100

                if label_name.lower() == 'unknown' or confidence < 95:
                    return Response({
                        "success": False,
                        "message": "عذراً، هذا التمثال غير مدعوم حالياً."
                    }, status=200)

                try:
                    statue_obj = Statue.objects.get(name=label_name)
                    statue_data = StatueSerializer(statue_obj).data

                    # ✅ حفظ في سجل البحث
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
                        "message": f"التمثال '{label_name}' غير مسجل في قاعدة البيانات."
                    }, status=200)

            return Response({"success": False, "message": "لا توجد نتائج."}, status=200)

        return Response({"success": False, "message": "Roboflow API Error"}, status=500)

    except Exception as e:
        logger.error(f"predict_artifact error: {e}")
        return Response({"success": False, "message": f"خطأ داخلي: {str(e)}"}, status=500)


# --- 4. ✅ جلب سجل البحث للمستخدم ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_search_history(request):
    history = SearchHistory.objects.filter(user=request.user).select_related('statue')[:20]
    serializer = SearchHistorySerializer(history, many=True, context={'request': request})
    return Response({
        "success": True,
        "history": serializer.data
    }, status=200)


# --- 5. ✅ بيانات المستخدم الحالي ---
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
