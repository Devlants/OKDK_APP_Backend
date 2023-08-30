from rest_framework import serializers
from .models import User
from django.conf import settings

class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["username","nickname","face_registered","mode",'image']

    def get_image(self,obj):
        if obj.image:
            return settings.PROJECT_HOST + obj.image.url
        else:
            return None
