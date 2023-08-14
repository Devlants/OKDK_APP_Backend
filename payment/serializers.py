from rest_framework import serializers
from .models import Card, History, Membership
from django.conf import settings

class CardDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    class Meta:
        model = Card
        fields = ["id","image","expiry_date","cvc","password","name","default","serial_num"]


    def get_name(self, instance):
        return instance.__str__()

    def get_image(self,instance):
        if instance.image:
            return str(getattr(settings,"PROJECT_HOST"))+str(instance.image.url)
        else:
            return None

class CardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ["expiry_date","cvc","password","serial_num"]

class CardSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    class Meta:
        model = Card
        fields = ["id","name","default","serial_num","image"]


    def get_name(self, instance):
        return instance.__str__()

    def get_image(self,instance):
        if instance.image:
            return str(getattr(settings,"PROJECT_HOST"))+str(instance.image.url)
        else:
            return None

class MembershipSerializer(serializers.ModelSerializer):
    brand = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    class Meta:
        model = Membership
        fields = ["id","brand","serial_num","image"]


    def get_brand(self, instance):
        brand = instance.brand.name
        return brand

    def get_image(self,instance):
        if instance.image:
            return str(getattr(settings,"PROJECT_HOST"))+str(instance.image.url)
        else:
            return None

class MembershipDetailSerializer(serializers.ModelSerializer):
    histories = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ["point","histories"]

    def get_histories(self,instance):
        histories = instance.history_set.all().order_by("-created_at")
        histories = HistorySerializer(histories,many=True).data
        return histories

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ["created_at","type","cur_total","point"]

