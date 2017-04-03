from django.contrib.auth.models import User
from rest_framework import serializers
from tourpoint.models import TourPoint


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
