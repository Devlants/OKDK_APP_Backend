from django.shortcuts import render
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
import requests

from coffee.models import Brand
from coffee.serializers import BrandSerializer
from .models import Card, History, Membership
from .serializers import CardSerializer, MembershipSerializer, MembershipDetailSerializer
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
        # new = Card(user = request.user, image = data["image"], serial_num = data["serial_num"],expiry_date = data["expiry_date"],cvc = data["cvc"],password = data["password"])
        new = Card(user = request.user, serial_num = data["serial_num"],expiry_date = data["expiry_date"],cvc = data["cvc"],password = data["password"])

        new.save()
        if data["is_default"] == True:
            new.set_default()
            new.save()
        return Response(status=200)

    def put(self,request):
        data = request.data
        card = Card.objects.get(id = data["id"])
        card.set_default()
        return Response(status=200)

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

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class MembershipCreateAPIView(APIView):
    def post(self,request):
        brand = Brand.objects.get(name = request.data.get("brand"))
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

