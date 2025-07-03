# -*- encoding: utf-8 -*-
# just one url
from django.urls import path
from mcms import views as mcms_views

urlpatterns = [
    path('', mcms_views.home, name='home'),
]
