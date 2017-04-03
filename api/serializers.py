from django.contrib.auth.models import User
from rest_framework import serializers
from tourpoint.models import TourPoint
from drf_haystack.serializers import HaystackSerializer
from api.search_indexes import TourPointLocationIndex


class TourPointSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        required=False,
        read_only=True)
    class Meta:
        model = TourPoint
        fields = ('url', 'name', 'category', 'owner', 'longitude', 'latitude', 'private')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    tourpoints = serializers.HyperlinkedIdentityField(
        view_name='user-tourpoints', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'tourpoints')


class DistanceSerializer(serializers.Serializer):
    km = serializers.FloatField()


class TourPointLocationSerializer(HaystackSerializer):
    distance = serializers.SerializerMethodField()

    class Meta:
        index_classes = [TourPointLocationIndex]
        fields = ['name', 'category', 'longitude', 'latitude', 'private', 'owner']

    def get_distance(self, obj):
        if hasattr(obj, "distance"):
            return DistanceSerializer(obj.distance, many=False).data
