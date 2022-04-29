from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient, Recipe
from recipe.serializers import IngredientSerializer, TagSerializer, RecipeSerializer, RecipeDetailSerializer, \
    RecipeImageSerializer
from rest_framework.response import Response
from rest_framework.decorators import action


class BaseRecipeAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """ Viewsets base """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """ Return objects for the authenticated user """
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

            return queryset.filter(
                user=self.request.user
             ).order_by('-name').distinct()

        return self.queryset.filter(user=self.request.user).order_by('name')

    def perform_create(self, serializer):
        """ Create new Tag """
        serializer.save(user=self.request.user)


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """ Tag handler in the database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        """ Return Tags objects for the authenticated user """
        return self.queryset.filter(user=self.request.user).order_by('name')

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
        return self.queryset.filter(user=self.request.user).order_by('name')

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
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def _params_to_ints(qs):
        """ Convert string list ids to ints list integers """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tags_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_ids)
        if ingredients:
            ingredients_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)

        return queryset.filter(user=self.request.user)
