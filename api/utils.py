import datetime
from django.core.cache import cache
from django.utils.encoding import force_text
from rest_framework_extensions.key_constructor.constructors import (
    DefaultKeyConstructor
)
from rest_framework_extensions.key_constructor.bits import (
    KeyBitBase,
    RetrieveSqlQueryKeyBit,
    ListSqlQueryKeyBit,
    PaginationKeyBit,
    QueryParamsKeyBit,
    UserKeyBit
)


class UpdatedAtKeyBit(KeyBitBase):
    """
    Custom key bit to look for api_updated_at_timestamp key.
    """
    def get_data(self, **kwargs):
        key = 'api_updated_at_timestamp'
        value = cache.get(key, None)
        if not value:
            value = datetime.datetime.utcnow()
            cache.set(key, value=value)
        return force_text(value)


class CustomObjectKeyConstructor(DefaultKeyConstructor):
    """
    Used to compute cache key for a single object.
    """
    retrieve_sql = RetrieveSqlQueryKeyBit()
    updated_at = UpdatedAtKeyBit()
    user = UserKeyBit()


class CustomListKeyConstructor(DefaultKeyConstructor):
    """
    Used to compute cache key for a list of objects.
    """
    list_sql = ListSqlQueryKeyBit()
    pagination = PaginationKeyBit()
    updated_at = UpdatedAtKeyBit()
    user = UserKeyBit()
    all_query_params = QueryParamsKeyBit()


def change_api_updated_at(sender=None, instance=None, *args, **kwargs):
    """
    Set a new timestamp for the cache.
    """

    cache.set('api_updated_at_timestamp', datetime.datetime.utcnow())


default_object_cache_key_func = CustomObjectKeyConstructor()
default_list_cache_key_func = CustomListKeyConstructor()

default_object_etag_func = default_object_cache_key_func
default_list_etag_func = default_list_cache_key_func
