from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter
from api import views
from api.views import FacebookLogin


router = SimpleRouter()
# users route
router.register(r'users', views.UserViewSet)
# tourpoint route

router.register(r'tourpoints', views.TourPointViewSet)
router.register(r'search', views.TourPointLocationGeoSearchViewSet,
                base_name='tourpoint-search')


urlpatterns = [
    url(r'^api/v1/', include([
        url(r'^', include(router.urls)),
        url(r'^auth/', include('rest_auth.urls', namespace='auth')),
        url(r'^auth/facebook/$', FacebookLogin.as_view(), name='facebook-login'),
        url(r'^$', views.APIRootView.as_view(), name='api-root'),
    ]))
]
