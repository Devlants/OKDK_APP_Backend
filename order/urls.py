from django.urls import path
from .views import *

urlpatterns = [
    path("favorite/",FavoriteAPIView.as_view(),name = "favorite"),
    path("recents/",RecentOrderApiView.as_view()),
    path("month/",MonthOrderApiView.as_view()),

]
