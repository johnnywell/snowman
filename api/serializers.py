from django.contrib.auth.models import User
from rest_framework import serializers
from tourpoint.models import TourPoint
from drf_haystack.serializers import HaystackSerializer
from api.search_indexes import TourPointLocationIndex
from api.validators import coodinates_validor


class TourPointSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the TourPoint model.
    """

    owner = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        required=False,
        read_only=True)

    class Meta:
        model = TourPoint
        fields = ('url', 'name', 'category', 'owner', 'longitude', 'latitude',
                  'private')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the User model.
    """
    tourpoints = serializers.HyperlinkedIdentityField(
        view_name='user-tourpoints', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'tourpoints')


class DistanceSerializer(serializers.Serializer):
    """
    Serilizer to validate the km param on the serach query.
    """
    km = serializers.FloatField()


class TourPointLocationSerializer(HaystackSerializer):
    """
    Serializer for the search request.
    """
    distance = serializers.SerializerMethodField()

    class Meta:
        index_classes = [TourPointLocationIndex]
        fields = ['name', 'category', 'longitude', 'latitude', 'private', 
                  'owner']

    def get_distance(self, obj):
        if hasattr(obj, "distance"):
            return DistanceSerializer(obj.distance, many=False).data


class SearchQueryParamsSerializer(serializers.Serializer):
    from_ = serializers.CharField(validators=[coodinates_validor])
    km = serializers.FloatField()


# workaround bacause the query parameter from is also a reserved python word.
SearchQueryParamsSerializer._declared_fields['from'] = SearchQueryParamsSerializer._declared_fields['from_']
del SearchQueryParamsSerializer._declared_fields['from_']
