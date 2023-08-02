from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
import requests
from coffee.models import Brand
from .models import Favorite

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class RecentOrderApiView(APIView):
    def get(self,request):
        recents = []
        data = {
            "user" : request.user.username
        }
        for brand in Brand.objects.all():
            api = brand.api
            response = requests.post(api+"order/list/",data = data)
            try:
                response = response.json()
            except:
                response = []
            recents+=response
        recents.sort(key = lambda x : x["created_at"],reverse = True)
        return Response(recents)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class MonthOrderApiView(APIView):
    def get(self,request):
        orders = []
        data = {
            "user" : request.user.username
        }
        for brand in Brand.objects.all():
            api = brand.api
            response = requests.post(api+"order/list/",data = data)
            try:
                response = response.json()
            except:
                response = []
            orders+=response
        orders.sort(key = lambda x : x["created_at"],reverse = True)
        data = {}
        for order in orders:
            month = order["created_at"][5:7]
            if month in data:
                data[month]["total"]+=order["totalPrice"]

            else:
                data[month] = {
                    "total" : 0,
                    "orders" : []
                }
            data[month]["orders"].append(order)

        return Response(data = data)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class FavoriteAPIView(APIView):
    def get(self,request):
        favorites = {}
        brands = Brand.objects.all()
        for brand in brands:
            api = brand.api
            if Favorite.objects.filter(brand = brand).exists():
                favorites[brand.name] = []

                #데이터 받아오기
                menues = []
                datas = requests.get(api+"menu/list/").json()
                for data in datas:
                    menues+=data["menues"]
                temperatures = requests.get(api+"order/temperature/list/").json()
                sizes = requests.get(api+"order/size/list/").json()

                for favorite in Favorite.objects.filter(brand = brand):
                    context = {}
                    context["menu"] = next((item for item in menues if item["id"] == favorite.menu), None)
                    context["temperature"] = next((item for item in temperatures if item["id"] == favorite.temperature), None)
                    context["size"] = next((item for item in sizes if item["id"] == favorite.size), None)
                    favorites[brand.name].append(context)

        return Response(favorites)

    def post(self,request):
        brand = Brand.objects.get(name = request.data["brand"])
        favorites = request.user.favorite_set.filter(brand = brand)
        for favorite in favorites:
            favorite.delete()

        menues = request.data["favorites"]
        for menu in menues:
            favorite = Favorite(user = request.user, brand = brand, menu = menu.get("menu"),temperature = menu.get("temperature"),size = menu.get("size"))
            favorite.save()

        return Response(status=200)



