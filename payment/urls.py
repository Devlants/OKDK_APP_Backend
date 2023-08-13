from django.urls import path
from .views import *

urlpatterns = [
    path("card/list/",CardListAPIView.as_view()),
    path("card/create/",CardCreateAPIView.as_view()),
    path("card/create/image/",CardImageCreateAPIView.as_view()),
    path("card/",CardAPIView.as_view()),
    path("membership/list/",MembershipListAPIView.as_view()),
    path("membership/history/",MembershipHistoryAPIView.as_view()),
    path("membership/",MembershipAPIView.as_view()),
    path("membership/create/",MembershipCreateAPIView.as_view()),

]
