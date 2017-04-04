from django.contrib.auth import get_user_model
from django.http import Http404
from django.db.models import Q
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from rest_framework import viewsets, permissions, views, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.reverse import reverse
from rest_framework_extensions.mixins import CacheResponseAndETAGMixin
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.etag.decorators import etag
from drf_haystack.viewsets import HaystackGenericAPIView
from drf_haystack.filters import HaystackGEOSpatialFilter, HaystackFilter
from haystack.query import SQ
from tourpoint.models import TourPoint
from api import serializers
from api.permissions import IsOwnerOrReadOnly
from api.utils import (
    default_object_cache_key_func,
    default_list_cache_key_func,
    default_object_etag_func,
    default_list_etag_func,
)


class APIRootView(views.APIView):
    @etag()
    @cache_response()
    def get(self, request, *args, **kwargs):
        data = {
            'users': reverse(
                'user-list', request=request, args=args, kwargs=kwargs,
                format=kwargs.get('format', None)),
            'tourpoints': reverse(
                'tourpoint-list', request=request, args=args, kwargs=kwargs,
                format=kwargs.get('format', None)),
            'facebook-auth': reverse(
                'facebook-login', request=request, args=args, kwargs=kwargs,
                format=kwargs.get('format', None)),
            'search': reverse(
                'tourpoint-search-list', request=request, args=args,
                kwargs=kwargs, format=kwargs.get('format', None)),
        }
        return Response(data)


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


class TourPointViewSet(CacheResponseAndETAGMixin, mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    queryset = TourPoint.objects.filter(private=False)
    serializer_class = serializers.TourPointSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    @etag(default_list_etag_func)
    @cache_response(key_func=default_list_cache_key_func)
    def list(self, request, format=None):
        if request.user.is_anonymous():
            queryset = TourPoint.objects.filter(category='restaurant', private=False)
        else:
            queryset = TourPoint.objects.filter(Q(Q(Q(private=True) & Q(owner=request.user)) | Q(private=False)))
        serializer = serializers.TourPointSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request, format=None):
        if request.user.is_anonymous():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = serializers.TourPointSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            # save the user from session as owner for this tour point
            serializer.validated_data['owner'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Allow users to delete their own tour points
        """
        instance = self.get_object()
        if instance.owner == request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)


class UserViewSet(CacheResponseAndETAGMixin, mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
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

    @etag(default_object_etag_func)
    @cache_response(key_func=default_object_cache_key_func)
    def retrieve(self, request, pk, format=None):
        user = self.get_object()
        serializer = serializers.UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @etag(default_list_etag_func)
    @cache_response(key_func=default_list_cache_key_func)
    @detail_route()
    def tourpoints(self, request, pk=None):
        tourpoints = self.get_object().tourpoints.filter(owner=request.user)
        page = self.paginate_queryset(tourpoints)
        if page is not None:
            serializer = serializers.TourPointSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = serializers.TourPointSerializer(
            tourpoints, many=True, context={'request': request})
        return Response(serializer.data)


class TourPointLocationGeoSearchViewSet(CacheResponseAndETAGMixin,
                                        mixins.ListModelMixin,
                                        viewsets.ViewSetMixin,
                                        HaystackGenericAPIView):
    index_models = [TourPoint]
    serializer_class = serializers.TourPointLocationSerializer
    filter_backends = [HaystackGEOSpatialFilter, HaystackFilter]

    @etag(default_list_etag_func)
    @cache_response(key_func=default_list_cache_key_func)
    def list(self, request, *args, **kwargs):
        # if there is no 'from' nor 'km' query parameters return a empty search.
        if request.query_params.get('from') and request.query_params.get('km'):
            if request.user.is_anonymous():
                # If a user is anonymous return only public restaurants
                queryset = self.filter_queryset(
                    self.get_queryset()).filter(
                        category='restaurant', private='false')
            else:
                # If the user is authenticated show all public and his own tour points.
                queryset = self.filter_queryset(self.get_queryset()).filter(SQ(SQ(SQ(private='true') & SQ(owner=request.user.username)) | SQ(private='false')))
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response([])
