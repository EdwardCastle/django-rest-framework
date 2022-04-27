from rest_framework import serializers
from core.models import Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """ Tag object serializer """

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """ Ingredient object serializer """

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)
