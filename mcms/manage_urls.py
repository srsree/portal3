# -*- encoding: utf-8 -*-
#just one url
from django.urls import path
from mcms import manage_views


# Admin home page url
# default admin url
urlpatterns = [
    path('', manage_views.home, name='manage-home'),
]
