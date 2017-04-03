from django.contrib.auth import get_user_model
import factory
from tourpoint import models


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'snowman%s' % n)


class TourPointFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TourPoint

    name = factory.Faker('name')
    longitude = -25.4230441
    latitude = -49.3084172
    private = factory.Iterator([True, False])
    owner = factory.SubFactory(UserFactory)
    category = factory.Iterator(['restaurant', 'park', 'museum'])
