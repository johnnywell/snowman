from django.contrib.auth.models import User
from rest_framework import serializers
from tourpoint.models import TourPoint


class TourPointSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedIdentityField(
        view_name='user-detail',
        required=False)
    class Meta:
        model = TourPoint
        fields = ('url', 'name', 'category', 'owner', 'longitude', 'latitude', 'private')


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username')
