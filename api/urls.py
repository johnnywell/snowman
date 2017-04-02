from django.conf.urls import url, include
from api.views import FacebookLogin
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    url(r'^docs/', include_docs_urls(title='Snow Man Labs Python Test')),
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^auth/facebook/$', FacebookLogin.as_view(), name='fb_login')
]
