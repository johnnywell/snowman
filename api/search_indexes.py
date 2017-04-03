from haystack import indexes
from tourpoint.models import TourPoint


class TourPointLocationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    category = indexes.CharField(model_attr='category')
    coordinates = indexes.LocationField(model_attr="coordinates")

    def get_model(self):
        return TourPoint