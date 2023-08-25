from rest_framework import serializers
from .models import Brand

class BrandSerializer(serializers.ModelSerializer):
    has_favorites = serializers.SerializerMethodField()
    class Meta:
        model = Brand
        fields = ["id","name"]

