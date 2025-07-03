#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This file contains user defined template tags to used templates to render values
"""

from mcms.models import *
from django import template
from django.http import HttpResponse
from django.shortcuts import render_to_response

from django.contrib.auth.models import *

import string
from collections import OrderedDict

from datetime import date, timedelta, datetime
from ccavenue.models import Subscription

import itertools
from faq.models import *
register = template.Library()

from dateutil.relativedelta import relativedelta

def yearsago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    return from_date - relativedelta(years=years)

@register.assignment_tag
def is_subscribed(request):
    today_date = datetime.now().date()
    subscribed = False
    prev_year_date = yearsago(1, today_date)
    user = request.user
    if not user.is_anonymous() and Editor.objects.filter(user__email=user.email):
        subscribed = True
    sub = ''
    if not user.is_anonymous():
        sub = Subscription.objects.filter(status="Success", email=user.email, created_on__gte=prev_year_date)
    if sub:
        subscribed = True
    return subscribed


@register.filter
def to_class_name(value):
    # to convert string into class name in template
    return value.__class__.__name__

@register.assignment_tag
def get_menus(request):
    # to get all menus excluding hall of fame 
    #return FrontMenu.objects.filter(id__in=[41,18,19,34,38,3])
    return FrontMenu.objects.filter(id__in=[41,2,7,34,38,17]).order_by('listingOrder')
    #return FrontMenu.objects.filter(active=True).exclude(id=13).order_by('listingOrder')[:6]

@register.assignment_tag
def get_rest_menus(request):
    # to get all menus excluding hall of fame 
    # excluding all menus comes from get_menus(request)
    return FrontMenu.objects.filter(active=True).order_by('listingOrder')[7:]

@register.assignment_tag
def get_all_menus(request):
    # get all menus which are active
    return FrontMenu.objects.filter(active=True).order_by('listingOrder')

@register.assignment_tag
def get_latest_article(request):
    # getting latest story of each menu
    return Article.objects.filter(active=True).latest('id')

@register.assignment_tag
def get_top_ad(request):
    # latest top position add
    try:
        return Ads.objects.filter(active=True, position="top").latest('id')
    except:
        return None

@register.assignment_tag
def get_center_ad(request):
    # latest top center add
    try:
        return Ads.objects.filter(active=True, position="center").latest('id')
    except:
        return None

@register.assignment_tag
def get_bottom_ad(request):
    # latest bottom position add
    try:
        return Ads.objects.filter(active=True, position="bottom").latest('id')
    except:
        return None

@register.assignment_tag
def get_columnists(request):
    # getting columnists to dispaly in sidebar
    try:
        return Columnists.objects.filter(active=True).order_by('?')
    except:
        return None

@register.assignment_tag
def get_current_issue(request):
    # getting current issue to dispaly in right sidebar
    try:
        return Currentissue.objects.filter(active=True).latest('id')
    except:
        return None

import urllib2
@register.assignment_tag
def get_rupee(d):
    # function to convert dollar into rupees
    # d : is number passing from template
    # by calling URL we will get output like this :'jQuery111004743527213577181_1449122965133({"success":true,"source":"USD","target":"INR","rate":66.852448,"amount":802.23,"message":""})'
    
    d = float(d)
    try:
        url = "https://currency-api.appspot.com/api/USD/INR.jsonp?amount="+str(d)+"&callback=jQuery111004743527213577181_1449122965133&_=1449122965138"
        response = urllib2.urlopen(url)
        html = response.read()
        html = str(html)
        amount_text = html[html.find('"amount":'):html.find(',"message"')]
        amount = float(amount_text.replace('"amount":',''))
    except:
        amount = float(d * 60)
    return amount


@register.assignment_tag
def get_countires():
    return Country.objects.all()


@register.filter
def dict_get(d, key):
    return d.get(key)