from rest_framework import serializers


def coodinates_validor(value):
    try:
        latitude, longitude = map(float, value.split(','))
    except:
        raise serializers.ValidationError(
            "The query parameter 'from' must be a comma separated latitude,"\
            "longitude .e.g. '-25.4230441,-49.3084172'.")
