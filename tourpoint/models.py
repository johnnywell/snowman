from django.db import models
from django.conf import settings


CATEGORIES = (
    ('restaurant', 'restaurant'),
    ('museum', 'museum'),
    ('park', 'park')
)


class TourPoint(models.Model):
    """
    A Tour Point created by users.
    """
    name = models.CharField(max_length=100,
                            help_text='Name for the tour point')
    longitude = models.FloatField(help_text='longitude for the current position')
    latitude = models.FloatField(help_text='latitude for the current position')
    private = models.BooleanField(
        default=False,
        help_text='To make this a private tour point')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='tourpoints',
        help_text="Who created this tour point.")
    category = models.CharField(choices=CATEGORIES,
                                max_length=10,
                                help_text='Which kind of tour point it is?')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
