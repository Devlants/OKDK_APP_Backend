import os

from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
import requests
import re
import pytesseract
from coffee.models import Brand
from coffee.serializers import BrandSerializer
from .models import Card, History, Membership
from .serializers import CardSerializer, MembershipSerializer, MembershipDetailSerializer, CardDetailSerializer, \
    CardCreateSerializer
from PIL import Image
from io import BytesIO
from django.core.files import File


@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class CardListAPIView(APIView):
    def get(self,request):
        cards = request.user.card_set.all()
        data = CardSerializer(cards,many = True).data
        return Response(data)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class CardAPIView(APIView):
    def post(self,request):
        data = request.data
        card = Card.objects.get(id=data["id"])
        serializer = CardDetailSerializer(card).data
        return Response(serializer)



@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class CardCreateAPIView(APIView):
    def post(self,request):
        data = request.POST
        new = Card(user = request.user, serial_num = data["serial_num"],expiry_date = data["expiry_date"],cvc = data["cvc"],password = data["password"])
        if request.FILES.get("image") != "":
            new.image = request.FILES.get("image")
        else:
            new.image = None
        new.save()
        if data["is_default"] == "true":
            new.set_default()
            new.save()
        return Response(status=200)

    def put(self,request):
        card = Card.objects.get(id = request.POST.get("id"))
        serializer = CardCreateSerializer(card, data=request.POST)
        if serializer.is_valid():
            card = serializer.save()
            card.image = request.FILES.get("image")
            if request.POST.get("is_default") == "true":
                card.set_default()
            card.save()

        return Response(status=200)

    def delete(self,request):
        data = request.data
        card = Card.objects.get(id = data["id"])
        card.delete()
        return Response(status=200)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class CardImageCreateAPIView(APIView):
    def post(self,request):
        image = request.data.get("image")
        # folder_path = "./media/card_create/"
        # image_path = os.path.join(folder_path, 'image.jpeg')
        # 이미지 로드
        image = Image.open(image)
        # 이미지 내의 텍스트 추출
        extracted_text = pytesseract.image_to_string(image)
        card_number = re.findall(r'\d{4} \d{4} \d{4} \d{4}', extracted_text)
        if card_number:
            card_number = card_number[0]
        else:
            card_number = None
        expiration_date = re.findall(r'\d{2}/\d{2}', extracted_text)
        if expiration_date:
            expiration_date = expiration_date[0]
        else:
            expiration_date = None
        cvc_number = re.findall(r'\d{3}', extracted_text)
        if cvc_number:
            cvc_number = cvc_number[0]
        else:
            cvc_number = None

        return Response({
            'card_number': card_number,
            'expiration_date': expiration_date,
            'cvc_number': cvc_number
        })

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class MembershipListAPIView(APIView):
    def get(self,request):
        memberships = request.user.membership_set.all()
        print(request.user)
        data = MembershipSerializer(memberships,many = True).data
        return Response(data)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class MembershipAPIView(APIView):
    def get(self,request):
            membership = list(request.user.membership_set.all().values_list("brand__id",flat=True))
            brands = Brand.objects.all().exclude(id__in = membership)
            data = BrandSerializer(brands,many = True).data

            return Response(data)

    def post(self,request):
        membership = request.user.membership_set.get(brand__name = request.data.get("brand"))
        data = MembershipDetailSerializer(membership).data
        return Response(data)

    def delete(self,request):
        try:
            membership = request.user.membership_set.get(brand__id = request.data.get("brand_id"))
            membership.delete()
            return Response(status = 200, data = {"message":"해당 매장의 멤버쉽이 삭제되었습니다."})
        except:
            return Response(status = 400, data = {"message":"해당 매장의 멤버쉽 정보가 없습니다."})





@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class MembershipCreateAPIView(APIView):
    def post(self,request):
        brand = Brand.objects.get(name = request.data.get("brand"))
        if Membership.objects.filter(user = request.user,brand = brand).exists():
            return Response({"error":"이미 존재하는 브랜드 입니다."},status = 400)

        new = Membership(user = request.user, brand = brand,serial_num = request.data.get("serial_num"))
        new.save()
        image = requests.get(f"http://bwipjs-api.metafloor.com/?bcid=code128&text={request.data.get('serial_num')}&scale=3&includetext&backgroundcolor=ffffff")
        barcode_image = Image.open(BytesIO(image.content))
        img_byte_array = BytesIO()
        barcode_image.save(img_byte_array, format='PNG')  # 다른 포맷으로 저장하려면 format 변경
        new.image.save(f"barcode_{new.pk}.png", File(img_byte_array))
        return Response(status=200)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class MembershipHistoryAPIView(APIView):
    def post(self,request):
        membership = request.user.membership_set.get(brand__name = request.data.get("brand"))
        history = History(membership = membership, point = request.data.get("point"),type = request.data.get("type"),cur_total = membership.point)
        history.save()
        if history.type == "적립":
            history.save_point()
        else:
            history.use_point()
        return Response(status = 200)

