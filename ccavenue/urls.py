from django.conf.urls import url
from ccavenue import views as ccavenue_views
# Ccavenue URLS
urlpatterns = [
    url(r'^subscribe/$', ccavenue_views.subscribe1, name='subscribe'),
    url(r'^subscribe2/$', ccavenue_views.subscribe2, name='subscribe'),   
    url(r'^subscribe/redirect/', ccavenue_views.subscribe_redirect, name='subscribe_redirect'),
    url(r'^subscribe/(?P<key>[a-zA-Z0-9_\ .,-]+)/$', ccavenue_views.subscribe1, name='key-subscribe'),
    url(r'^subscribe/hindi/(?P<key>[a-zA-Z0-9_\ .,-]+)/$', ccavenue_views.subscribe3, name='key-subscribe'),
    url(r'^bookshopdetail/$', ccavenue_views.bookshopsubscribe, name='bookshopsubscribe'),
]
