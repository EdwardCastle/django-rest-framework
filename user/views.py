from user.serializers import UserSerializer
from rest_framework import generics


class CreateUserView(generics.CreateAPIView):
    """ Create a new User in the system """

    serializer_class = UserSerializer