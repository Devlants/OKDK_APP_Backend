from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("kakao/callback/",KaKaoCallBackView.as_view(),name = "kakao-login-callback"),
    path("naver/callback/",NaverCallBackView.as_view(),name = "naver-login-callback"),
    path("google/",GoogleView.as_view(),name = "google_login"),
    path("google/callback/",GoogleCallBackView.as_view(),name = "google-login-callback"),
    path("refresh/access_token/",RefreshAccessTokenAPIView.as_view(),name = "refresh_access_token"),

    path("user/",UserInfoAPIView.as_view(),name = "user_info"),
    path("user/mode/update/",UserModeUpdateAPIView.as_view(),name = "user-mode-update"),
    path("user/default/card/",DefaultCardAPIView.as_view()),
    path("user/membership/",MembershipApiView.as_view()),
    path("user/face/recognition/",FaceRecognitionApiView.as_view()),
    path("user/face/register/",FaceRegisterAPIView.as_view()),
]
