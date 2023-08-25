from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
import requests
from coffee.models import Brand
from coffee.serializers import BrandSerializer



@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class BrandList(APIView):
    def get(self,request):
        user_favorites = list(set(list(request.user.favorite_set.all().values_list("brand__id",flat = True))))
        context = {
            "user_favorites" : user_favorites
        }
        brands = Brand.objects.all()
        brands = BrandSerializer(brands,many=True,context = context).data

        return Response(brands)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class BrandMenuAPIView(APIView):
    def get(self, request,**kwargs):
        brand = Brand.objects.get(id = kwargs["id"])
        data = requests.get(brand.api+"menu/list/").json()
        menues = []
        for d in data:
            menues+=d['menues']
        return Response(menues)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class BrandTemperatureAPIView(APIView):
    def get(self, request,**kwargs):
        brand = Brand.objects.get(id = kwargs["id"])
        data = requests.get(brand.api+"order/temperature/list/").json()
        temperatures = []

        for d in data:
            temperatures.append(d)
        return Response(temperatures)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class BrandSizeAPIView(APIView):
    def get(self, request,**kwargs):
        brand = Brand.objects.get(id = kwargs["id"])
        data = requests.get(brand.api+"order/size/list/").json()
        sizes = []

        for d in data:
            sizes.append(d)
        return Response(sizes)



