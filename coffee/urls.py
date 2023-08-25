from django.urls import path
from .views import *

urlpatterns = [
    path("brand/list/",BrandList.as_view()),
    path("brand/<int:id>/menu/list/",BrandMenuAPIView.as_view()),
    path("brand/<int:id>/temperature/list/",BrandTemperatureAPIView.as_view()),
    path("brand/<int:id>/size/list/",BrandSizeAPIView.as_view()),

]
