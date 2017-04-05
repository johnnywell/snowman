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
    """
    To explore this API you may login using the button on the top of this page.

    **The default user is:**

        username: snowman
        password: snowmanlabs

    For details about other resources and how to use them folow the links below.

    ## Request


    ### List GET: /api/<version\>/


    ## Response

    Returns a index with the main resources for this API.
    """
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
    Check a given Facebook Acess Token and return a new Key if the credentials\
    are valid and authenticated.

    Use this key to authenticate the user from now on by setting the request \
    headers as follow:

    **Authentication: Token 2d9b3a087acd31c4a36e016fff72869582590166**

    If the user does not exist it is created and added to the session. You may
    also take advantage of cookies to refer to the given session id, so you \
    don't need to pass the Token on further requests.

    ## Request

    ### Create POST: /api/<version\>/auth/facebook/

        {
            'access_token':'EAAED1a2VBqYBAEFHGKsYUH9jzm4KsfZAK54y5A5DZB5IMxKXDa
                KOmi0mZAGRFZAGf9ZBLHUenOyDm8tVJdt133YwwJsTz3ttu8b2pOAZAdL82tgNb
                TTAzGh1ROrgX9XasBZBIpLJERP5pns2MZAa3AIUZBmlfDOhTmeQCoiWoJo51aZA
                nWjH3nEdk8MfYBwYerzX0ZD'
        }

    ## Response

        {
            'key': '2d9b3a087acd31c4a36e016fff72869582590166'
        }
    """
    adapter_class = FacebookOAuth2Adapter


class TourPointViewSet(CacheResponseAndETAGMixin, mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """
    ## Requests

    ### List GET: /api/<version\>/tourpoints/

    #### Response

    If the user is authenticated returns a list of public and his own private \
    tour points from every category.

    If the user is anonymous returns only public restaurants.


    ### Retrieve GET: /api/<version\>/tourpoints/<pk\>/

    #### Response

    Returns a tour point given its id.

    ### Create POST: '/api/<version\>/tourpoints/<pk\>/'

    To create a new tour point use this resource ass follow.

        {
            'name': 'Barigui Park',
            'category': 'park',
            'private': false,
            'longitude': -25.4230441,
            'latitude': -49.3084172
        }

    The user will be determined by the request and set as owner for this tour \
    point.

    Only authenticated users can create tour points.

    #### Response

    The response contais the data provided and also links for this same \
    resource and its owner as well.

        {
            "url": "http://localhost/api/v1/tourpoints/1/",
            "name": "snowman",
            "category": "park",
            "owner": "http://localhost/api/v1/users/1/",
            "longitude": -25.4230441,
            "latitude": -49.3084172,
            "private": false
        }

    ### Destroy DELETE: /api/<version\>/tourpoints/<pk\>/

    Authenticated users may also delete his own tour points.


    #### Response

    The response for a successful destroy request is a 204 NO CONTENT code, \
    indicating this tour point is no more.
    """
    queryset = TourPoint.objects.filter(private=False)
    serializer_class = serializers.TourPointSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    @etag(default_list_etag_func)
    @cache_response(key_func=default_list_cache_key_func)
    def list(self, request, format=None):
        if request.user.is_anonymous():
            queryset = TourPoint.objects.filter(
                category='restaurant', private=False)
        else:
            queryset = TourPoint.objects.filter(
                Q(Q(Q(private=True) & Q(
                    owner=request.user)) | Q(private=False)))
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
    """
    The two following requests only returns the currently authenticated user, \
    for simplicity purpose.

    ## Retrieve GET: /api/<version\>/users/<pk\>/

    ## List GET: /api/<version\>/users/

    ---

    ## List GET: /api/<version\>/users/<pk\>/tourpoints/

    This resource returs a list with all tour points created by the user.

    It is worth to notice that the user is reevaluated on the session, and
    the resource only returns information for the authenticated user.

    """
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
        serializer = serializers.UserSerializer(
            user, context={'request': request})
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
    """
    ## Request GET: /api/<version\>/search/?from=<long\>,<lat\>&km=<ditance\>

    This resource searchs for tour points in a radius given a position.

    **The query parameters must be as follow:**

        from=-25.4230441,-49.3084172    # comma separated longitude and latitude 
        km=5                            # a radius distance in kilometers

    ### Resonse

    The response will be a list of tour point objects in the same format as \
    follow.

        {
            "name": "Melissa Wang",
            "category": "park",
            "private": true,
            "longitude": -25.4230441,
            "latitude": -49.3084172,
            "owner": "snowman",
            "distance": {
                "km": 0.0
            }
        }

    This resource also follow the same rules for anonymous or authenticated \
    users as described in [tour points list](/api/v1/tourpoints/) resource

    If any query parameter is missing the response will be empty.
    """
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
                # If the user is authenticated show all public and his own tour
                # points.
                queryset = self.filter_queryset(
                    self.get_queryset()).filter(
                        SQ(SQ(SQ(private='true') & SQ(
                            owner=request.user.username)) | SQ(
                                private='false')))
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response([])
