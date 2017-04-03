from haystack import indexes
from tourpoint.models import TourPoint


class TourPointLocationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    name = indexes.CharField(model_attr='name')
    category = indexes.CharField(model_attr='category')
    coordinates = indexes.LocationField(model_attr="coordinates")
    private = indexes.BooleanField(model_attr='private')
    longitude = indexes.FloatField(model_attr='longitude')
    latitude = indexes.FloatField(model_attr='latitude')
    owner = indexes.CharField(model_attr='owner')

    def get_model(self):
        return TourPoint