import requests
import base64
import logging
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Statue, SearchHistory
from .serializers import StatueSerializer

# إعداد الـ Logger
logger = logging.getLogger(__name__)

# بيانات مشروع Roboflow
ROBOFLOW_API_KEY = "0Q95f8rFPiohq2RfJuR9"
MODEL_ID = "egyptian-statues/4" 

@api_view(['POST'])
@permission_classes([IsAuthenticated]) # أضفنا دي عشان نضمن إن اللي بيبحث لازم يكون عامل Login
@parser_classes([MultiPartParser, FormParser]) # لضمان معالجة الصور المرفوعة من Flutter بشكل صحيح
def predict_artifact(request):
    """
    تستلم الصورة، ترسلها لـ Roboflow، تبحث عن النتيجة في الداتابيز، 
    وتسجل العملية في سجل البحث الخاص بالمستخدم الحالي.
    """
    
    # 1. التأكد من وجود ملف الصورة
    if 'image' not in request.FILES:
        return Response({
            "success": False, 
            "message": "لم يتم استلام صورة."
        }, status=400)

    try:
        image_file = request.FILES['image']
        image_bytes = image_file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # 2. إرسال طلب Roboflow
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
                
                # فلترة الهبد
                if label_name.lower() == 'unknown' or confidence < 95: 
                    return Response({
                        "success": False, 
                        "message": "عذراً، هذا التمثال غير مدعوم حالياً أو الصورة غير واضحة."
                    }, status=200)

                # 3. البحث عن بيانات التمثال في الداتابيز
                try:
                    statue_obj = Statue.objects.get(name=label_name)
                    statue_data = StatueSerializer(statue_obj).data
                    
                    # 4. تسجيل العملية في السجل (Search History) 
                    # بما أننا استخدمنا IsAuthenticated، فـ request.user مضمون وجوده
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
                        "message": f"تم التعرف على {label_name} ولكن بياناته غير مسجلة في الداتابيز."
                    }, status=200)
            
            return Response({"success": False, "message": "لم يتم العثور على نتائج."}, status=200)

        return Response({"success": False, "message": "API Error from Roboflow"}, status=500)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return Response({"success": False, "message": f"خطأ داخلي: {str(e)}"}, status=500)