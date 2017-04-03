from django.conf.urls import include, url
from rest_framework.documentation import include_docs_urls
from rest_framework_extensions.routers import (
    ExtendedDefaultRouter as DefaultRouter
)
from api import views
from api.views import FacebookLogin

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'tourpoints', views.TourPointViewSet)
router.register(r'search', views.TourPointLocationGeoSearchViewSet, 
                base_name='tourpoint-search')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^auth/facebook/$', FacebookLogin.as_view(), name='fb_login'),
    url(r'^docs/', include_docs_urls(title='Snow Man Labs Python Test')),
]