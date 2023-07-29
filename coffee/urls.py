from django.urls import path
from .views import *

urlpatterns = [
    path("brand/nonFavorite/list/",BrandNotFavoriteAPIView.as_view()),
    path("brand/<int:id>/menu/list/",BrandMenuAPIView.as_view()),

]
