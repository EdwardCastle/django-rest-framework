from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient, Recipe
from recipe.serializers import IngredientSerializer, TagSerializer, RecipeSerializer


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """ Tag handler in the database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        """ Return Tags objects for the authenticated user """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """ Create new Tag """
        serializer.save(user=self.request.user)


class IngredientViewset(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """ Ingredient handler in the database """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        """ Return Ingredients objects for the authenticated user """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """ Create new Ingredient """
        serializer.save(user=self.request.user)


class RecipeViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """ Recipe handler in the database """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        """ Return Ingredients objects for the authenticated user """
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """ Create new Ingredient """
        serializer.save(user=self.request.user)
