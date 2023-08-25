from rest_framework import serializers
from .models import Brand

class BrandSerializer(serializers.ModelSerializer):
    has_favorites = serializers.SerializerMethodField()
    class Meta:
        model = Brand
        fields = ["id","name","has_favorites"]

    def get_has_favorites(self,obj):
        if obj.id in self.context:
            return True
        else:
            return False
