from django.contrib.auth import get_user_model
from django.http import Http404
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from rest_framework import viewsets, permissions, generics, views, status
from rest_framework.response import Response

from tourpoint.models import TourPoint
from api import serializers
from api.permissions import IsOwnerOrReadOnly


class FacebookLogin(SocialLoginView):
    """
    post:
    Check a given Facebook Acess Token and return a new Key if the credentials\
    are valid and authenticated.
    
    Use this key to authenticate the user from now on.
    
    If the user does not exist it is created.

    **Accept**: access_token

    **Return**: key
    """
    adapter_class = FacebookOAuth2Adapter


class TourPointViewSet(viewsets.ModelViewSet):
    queryset = TourPoint.objects.filter(private=False)
    serializer_class = serializers.TourPointSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def list(self, request, format=None):
        queryset = TourPoint.objects.all()
        serializer = serializers.TourPointSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)


    def create(self, request, format=None):
        serializer = serializers.TourPointSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            # save the user from session as owner for this tour point
            serializer.validated_data['owner'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return get_user_model().objects.filter(id=self.request.user.pk)

    def get_object(self):
        try:
            return get_user_model().objects.get(id=self.request.user.pk)
        except get_user_model().DoesNotExist:
            raise Http404

    def retrieve(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = serializers.UserSerializer(user, context={'request': request})
        return Response(serializer.data)

