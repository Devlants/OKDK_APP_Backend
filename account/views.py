from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from payment.serializers import CardSerializer, MembershipSerializer
from .models import User
from .serializers import UserSerializer
import requests
from django.core.exceptions import ValidationError
import json
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

@permission_classes((AllowAny,))
class KaKaoView(APIView):
    def get(self, request):
        kakao_api = "https://kauth.kakao.com/oauth/authorize?response_type=code&client_id="
        redirect_uri = "http://3.38.180.187/account/kakao/callback/"
        client_id = "1def2aa86fd42c81904840220886ac54"
        print(requests.get(f"{kakao_api}{client_id}&redirect_uri={redirect_uri}").json())
        return requests.get(f"{kakao_api}{client_id}&redirect_uri={redirect_uri}").json()

@permission_classes((AllowAny,))
class KaKaoCallBackView(APIView):
    def get(self, request):

        data = {
            "grant_type": "authorization_code",
            "client_id": "1def2aa86fd42c81904840220886ac54",
            "redirect_uri" : "http://3.38.180.187/account/kakao/callback/",
            "code" : request.GET["code"]
        }

        kakao_token_api = "https://kauth.kakao.com/oauth/token"

        ACCESS_TOKEN = requests.post(kakao_token_api,data = data).json()["access_token"]

        kakao_user_api = "https://kapi.kakao.com/v2/user/me"
        headers = {
            "Authorization":f"Bearer ${ACCESS_TOKEN}",
            "Content-type" : "application/x-www-form-urlencoded;charset=utf-8"
        }
        user_info = requests.get(kakao_user_api,headers = headers).json()

        username = user_info["id"]
        nickname = user_info["properties"]["nickname"]
        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, password=None, nickname = nickname)

        # 로그인 처리
        refresh = RefreshToken.for_user(user)

        return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })

@permission_classes((AllowAny,))
class NaverView(APIView):
    def get(self, request, *args, **kwargs):
        client_id = "oRQ7F4q_jX8AvonjIVNf"
        response_type = "code"
        uri = "http://3.38.180.187/account/naver/callback/"
        state = "NAVER_LOGIN_STRING"
        # Naver Document 에서 확인했던 요청 url
        url = "https://nid.naver.com/oauth2.0/authorize"

        # Document에 나와있는 요소들을 담아서 요청한다.
        return redirect(
            f'{url}?response_type={response_type}&client_id={client_id}&redirect_uri={uri}&state={state}'
        )

@permission_classes((AllowAny,))
class NaverCallBackView(APIView):

    def get(self, request, *args, **kwargs):
        naver_token_api = "https://nid.naver.com/oauth2.0/token"
        token = request.GET["code"]
        data = {
            "grant_type" : "authorization_code",
            "client_id" : "oRQ7F4q_jX8AvonjIVNf",
            "client_secret" : "jA2auTdVIo",
            "code" : token
        }
        ACCESS_TOKEN = requests.post(naver_token_api,data = data).json()["access_token"]
        header = {
            "Authorization" : "Bearer " + ACCESS_TOKEN
        }
        url = "https://openapi.naver.com/v1/nid/me"

        response = requests.get(url,headers = header).json()
        username = response["response"]["email"]
        name = response["response"]["name"]

        try:
            user = User.objects.get(username = username)
        except:
            user = User.objects.create_user(username=username, password=None, nickname = name)

        refresh = RefreshToken.for_user(user)

        return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })

@permission_classes((AllowAny,))
class GoogleView(APIView):
    def get(self, request):
        app_key = "435546094465-nkivfk3cju2jg1jp1katfsu5ttbfkgti.apps.googleusercontent.com"
        scope = "https://www.googleapis.com/auth/userinfo.email " + \
                "https://www.googleapis.com/auth/userinfo.profile"

        redirect_uri = "http://ec2-3-38-180-187.ap-northeast-2.compute.amazonaws.com/account/google/callback/"
        google_auth_api = "https://accounts.google.com/o/oauth2/v2/auth"

        response = redirect(
            f"{google_auth_api}?client_id={app_key}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
        )

        return response

@permission_classes((AllowAny,))
class GoogleCallBackView(APIView):
    def get(self, request, *args, **kwargs):

        google_token_api = "https://oauth2.googleapis.com/token"

        client_id = "435546094465-nkivfk3cju2jg1jp1katfsu5ttbfkgti.apps.googleusercontent.com"
        client_secret = "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"
        code = request.GET.get('code')
        grant_type = 'authorization_code'
        redirection_uri = "http://ec2-3-38-180-187.ap-northeast-2.compute.amazonaws.com/account/google/callback/"
        state = "random_string"

        google_token_api += \
            f"?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type={grant_type}&redirect_uri={redirection_uri}&state={state}"

        token_response = requests.post(google_token_api)

        if not token_response.ok:
            raise ValidationError('google_token is invalid')

        access_token = token_response.json().get('access_token')
        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            params={
                'access_token': access_token
            }
        )

        if not user_info_response.ok:
            raise ValidationError('Failed to obtain user info from Google.')

        user_data = user_info_response.json()

        username = user_data['email']
        name =  user_data.get('name')

        try:
            user = User.objects.get(username = username)
        except:
            user = User.objects.create_user(username=username, password=None, nickname = name)

        refresh = RefreshToken.for_user(user)

        return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })

@permission_classes((AllowAny,))
class RefreshAccessTokenAPIView(APIView):
    def post(self,request):
        refresh_token = json.loads(request.body)["refresh"]
        if not refresh_token:
            return Response({'error': 'Refresh 토큰이 필요합니다'}, status=401)

        try:
            refresh_token = RefreshToken(refresh_token)
            access_token = str(refresh_token.access_token)

            return Response({'access': access_token,'refresh':str(refresh_token)})
        except Exception as e:
            return Response({'error': '유효하지 않은 Refresh 토큰'}, status=401)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class UserInfoAPIView(APIView):
    def get(self,request):
        serializer = UserSerializer(instance=request.user)
        return Response(serializer.data)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class UserModeUpdateAPIView(APIView):
    @method_decorator(csrf_exempt)
    def put(self, request):
        data = json.loads(request.body)
        user = get_object_or_404(User,username = data["username"])
        user.mode = "easy" if user.mode == "normal" else "normal"
        user.save()
        serializer = UserSerializer(instance = user)
        return Response(serializer.data)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class DefaultCardAPIView(APIView):
    def get(self,request):
        if request.user.card_set.filter(default = True).exists():
            data = CardSerializer(request.user.card_set.get(default = True)).data
        else:
            data = {
                "name" : None,
                "serial_num" : None
            }
        return Response(data)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class MembershipApiView(APIView):
    def get(self,request):
        if request.user.membership_set.filter(brand__name = request.GET.get("brand")).exists():
            data = MembershipSerializer(request.user.membership_set.get(brand__name = request.GET.get("brand"))).data
        else:
            data = {
                "serial_num" : None
            }
        return Response(data)



