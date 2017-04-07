from django.contrib.auth import get_user_model
from django.db.models import Q
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from rest_framework import viewsets, permissions, views, mixins
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.reverse import reverse
from rest_framework_extensions.mixins import CacheResponseAndETAGMixin
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.etag.decorators import etag
from rest_framework.permissions import IsAuthenticatedOrReadOnly
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
    queryset = TourPoint.objects.all()
    serializer_class = serializers.TourPointSerializer
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly)

    def get_queryset(self):
        """
        If a user is anonymous returns only, public restrautants, otherwise
        returns all public tour points and his own private ones.
        """
        if self.request.user.is_anonymous():
            queryset = self.queryset.filter(
                category='restaurant', private=False)
        else:
            queryset = self.queryset.filter(
                Q(Q(Q(private=True) & Q(
                    owner=self.request.user)) | Q(private=False)))
        return queryset

    def perform_create(self, serializer):
        """
        Override the super method to add the request user as the owner.
        """
        serializer.validated_data['owner'] = self.request.user
        super().perform_create(serializer)


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
        """
        Returns only the authenticated user, since we don't need users to
        interact with other users.
        """
        return get_user_model().objects.filter(id=self.request.user.pk)

    @etag(default_list_etag_func)
    @cache_response(key_func=default_list_cache_key_func)
    @detail_route()
    def tourpoints(self, request, pk=None):
        """
        Custom action to list a user tour points.
        Since we filter the queryset for the request user it only returns the
        tour points for that user, but it can be easily changed to return a
        list for a given user if we need to.
        """
        tourpoints = self.get_object().tourpoints.all()
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

    def filter_queryset(self, queryset):
        """
        Override super filter_queryset to apply our bussiness logic. Since it
        is a public resource we don't need further permissions, just valitate
        if the user is authenticated or not.
        """
        # First validate the query params, so whe are sure they are provided.
        params_serializer = serializers.SearchQueryParamsSerializer(
            data=self.request.query_params)
        params_serializer.is_valid(raise_exception=True)

        # apply the super filter to the queryset, so now we have only objects
        # respecting the radius search.
        queryset = super().filter_queryset(queryset)

        # If a user is anonymous return only public restaurants
        if self.request.user.is_anonymous():
                queryset = queryset.filter(
                        category='restaurant', private='false')
        else:
            # If the user is authenticated show all public and his own tour
            # points.
            queryset = queryset.filter(
                    SQ(SQ(SQ(private='true') & SQ(
                        owner=self.request.user.username)) | SQ(
                            private='false')))
        return queryset

