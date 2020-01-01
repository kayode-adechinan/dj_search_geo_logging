from rest_framework import serializers
from core import models



class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = models.Author


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = models.Post


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = models.Tag




class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = models.Shop