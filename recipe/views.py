from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient, Recipe
from recipe.serializers import IngredientSerializer, TagSerializer, RecipeSerializer, RecipeDetailSerializer, \
    RecipeImageSerializer
from rest_framework.response import Response
from rest_framework.decorators import action


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


class RecipeViewSet(viewsets.ModelViewSet):
    """ Recipe handler in the database """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        """ Return Ingredients objects for the authenticated user """
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """ Return the apropied serializer """

        if self.action == 'retrieve':
            return RecipeDetailSerializer

        elif self.action == 'upload-image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ Create new Ingredient """
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """ Upload image to recipe """
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            print('a')

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
