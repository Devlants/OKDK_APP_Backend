from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from payment.models import Card
from payment.serializers import CardSerializer, MembershipSerializer
from .models import User
from .serializers import UserSerializer
import requests
from django.core.exceptions import ValidationError
import json
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
import face_recognition
import os
import numpy as np
from PIL import Image
import re

@permission_classes((AllowAny,))
class KaKaoCallBackView(APIView):
    def get(self, request):
        print("hi")
        data = {
            "grant_type": "authorization_code",
            "client_id": "1def2aa86fd42c81904840220886ac54",
            "redirect_uri" : "https://voluble-basbousa-74cfc0.netlify.app/",
            # "redirect_uri" : "http://127.0.0.1:3000/kakao/callback/",
            "code" : request.GET["code"]
        }

        kakao_token_api = "https://kauth.kakao.com/oauth/token"
        print(requests.post(kakao_token_api,data = data).json())
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
        access_token = request.GET.get('access_token')
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
        serializer = UserSerializer(instance=request.user).data
        username = serializer.get("username")
        if username.isdigit():
            social = "카카오톡"
        elif re.compile(r"@gmail\.com$").search(username) is not None:
            social = "구글"
        else:
            social = "네이버"
        data = {
            "social" : social,
            "user" : serializer
        }
        return Response(data)

    def delete(self,request):
        user = request.user
        user.delete()
        return Response(status = 200)

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

    def put(self,request):
        data = request.data
        card = Card.objects.get(id = data["id"])
        card.set_default()
        return Response(status=200)

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

class FaceRecog():
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []

        # Load sample pictures and learn how to recognize them.
        dirname = 'media/user'
        files = os.listdir(dirname)
        for filename in files:
            print(filename)
            name, ext = os.path.splitext(filename)
            if ext == '.jpg':
                self.known_face_names.append(name)
                pathname = os.path.join(dirname, filename)
                img = face_recognition.load_image_file(pathname)
                print(img)
                print(face_recognition.face_encodings(img))
                face_encoding = face_recognition.face_encodings(img)[0]
                self.known_face_encodings.append(face_encoding)

    def recognize_faces_in_image(self, image_path):
        # Load the image
        image = face_recognition.load_image_file(image_path)
        print("image",image)
        # Find all the faces and face encodings in the image
        face_locations = face_recognition.face_locations(image)
        print("face_locations",face_locations)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            # Compare the face with known faces
            distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            min_value = min(distances)
            # tolerance: How much distance between faces to consider it a match. Lower is more strict.
            # 0.6 is typical best performance.
            name = "Unknown"
            if min_value < 0.6:
                index = np.argmin(distances)
                name = self.known_face_names[index]

            face_names.append(name)
            return name

@permission_classes((AllowAny,))
class FaceRecognitionApiView(APIView):
    def post(self,request):

        if not os.listdir("./media/user/"):
            return Response(status=400,data = {"error":"얼굴 등록 정보가 없습니다."})

        if "image" not in request.data or not request.data["image"]:
            return Response(status=400,data = {"error":"사진 데이터 없음"})
        image = request.data.get("image")
        folder_path = "./media/unknown/"
        image_path = os.path.join(folder_path, 'image.jpeg')

        face_recog = FaceRecog()
        print("init FaceRecog()")
        print("image :",image)
        with Image.open(image) as img:
            print("img opened")
            if hasattr(img, "_getexif"):
                exif = img._getexif()
                if exif is not None:
                    orientation = exif.get(0x0112, 1)
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
            img = img.convert("RGB")
            print("img converted")
            img.save(image_path, format='JPEG', quality=90)
            print(image_path,"img saved")
        username = face_recog.recognize_faces_in_image(image_path)
        print("username",username)
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            os.remove(item_path)
        try:
            user = User.objects.get(username = username)
            print("user",user)
        except:
            print("unknown user")
            return Response(status = 401, data = {"error" : "Unknown user"})

        refresh = RefreshToken.for_user(user)

        return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
##
@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class FaceRegisterAPIView(APIView):
    def post(self,request):
        if request.user.face_registered:
            return Response(status = 400,data = {"message": "이미 등록된 얼굴이 있음"})

        image = request.data.get("image")
        folder_path = "./media/unknown/"
        image_path = os.path.join(folder_path, 'image_register.jpeg')

        with Image.open(image) as img:
            # Check and adjust orientation if needed
            if hasattr(img, "_getexif"):
                exif = img._getexif()
                if exif is not None:
                    orientation = exif.get(0x0112, 1)
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
            img = img.convert("RGB")
            img.save(image_path, format='JPEG', quality=90)

        image_check =  face_recognition.face_locations(face_recognition.load_image_file(image_path))
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            os.remove(item_path)

        if image_check:
            unique_filename = request.user.username + os.path.splitext(image.name)[-1]
            request.user.image.save(unique_filename, image)
            request.user.face_registered = True
            request.user.save()
            return Response(status = 200)
        else:
            return Response(status = 400, data = {"message" : "사진 불량"})

    def put(self,request):
        if not request.user.face_registered:
            return Response(status = 400,data = {"message": "등록된 얼굴이 없음"})

        image = request.data.get("image")
        folder_path = "./media/unknown/"
        image_path = os.path.join(folder_path, 'image_register.jpeg')

        with Image.open(image) as img:
            # Check and adjust orientation if needed
            if hasattr(img, "_getexif"):
                exif = img._getexif()
                if exif is not None:
                    orientation = exif.get(0x0112, 1)
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
            img = img.convert("RGB")
            img.save(image_path, format='JPEG', quality=90)

        image_check =  face_recognition.face_locations(face_recognition.load_image_file(image_path))
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            os.remove(item_path)

        if image_check:
            for item in os.listdir("./media/user/"):
                item_path = os.path.join('./media/user/', item)
                os.remove(item_path)
            unique_filename = request.user.username + os.path.splitext(image.name)[-1]
            request.user.image.save(unique_filename, image)
            request.user.face_registered = True
            request.user.save()
            return Response(status = 200)
        else:
            return Response(status = 400, data = {"message" : "사진 불량"})
