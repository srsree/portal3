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
from mcms.CryptoHashCode import tohashval

import string
from collections import OrderedDict

from datetime import date, timedelta

import itertools
from faq.models import *

register = template.Library()
eng_lang = Language.objects.get(name="English")

@register.assignment_tag
def get_hash_value(val):
    return tohashval(val)

@register.filter
def get_user_answer(request):
    check = False
    user = User.objects.get(pk = request.user.pk)
    content_type = ContentType.objects.get_for_model(user)
    hist = Assessment_Frequency_History.objects.filter(content_type = content_type, object_id = user.pk)
    asfrq = Assessment_Frequency.objects.all()[0]
    if len(hist) == asfrq.count:
        check = True
    return check


@register.filter
def get_menu_access_list(request):
    menu_list = []
    try:
        user_obj = User.objects.get(id=int(request.user.id))
        ad_obj = user_obj.admin_user_set.all()[0]
        amenu = MenuRole_Permission.objects.get(admin_user__id = int(ad_obj.id))
        for i in amenu.role.permissions.all():
            menu_list.append(str(i.name))
    except:
        pass
    return menu_list


@register.assignment_tag
def get_user_used(request, state, used_list):
    user_list = []
    for usr in used_list:
        if state == usr.state:
            user_list.append(usr.assigned_user)
    return list(set(user_list))


@register.assignment_tag
def check_menu_perm(request,tlist):
    status , menu_list = False, []
    try:
        user_obj = User.objects.get(id=int(request.user.id))
        if not user_obj.is_superuser:
            ad_obj = user_obj.admin_user_set.all()[0]
            amenu = MenuRole_Permission.objects.get(admin_user__id = int(ad_obj.id))
            for i in amenu.role.permissions.all():
                menu_list.append(str(i.name))
            if tlist in menu_list:
                status = True
        else:
            status = True
    except:
        status = False
    return status

@register.filter
def get_expert_speak(request):
    domain = sub_domain(request)
    expert_list = ''
    if domain == "english" or domain == "wsfdemo" or domain == 'localhost8000' or domain == "whiteswandemo":
        expert_list = Experts_Speak_Profile.objects.filter(active=True, language=eng_lang).order_by('-id')
    else:
        expert_list = Experts_Speak_Profile.objects.filter(active=True, language__slug =str(domain)).order_by('-id')
    return expert_list


@register.filter
def get_tips(request):
    tips_list = Tips.objects.filter(active=True)
    return tips_list


@register.filter
def get_workflow_count(request):
    countDict = OrderedDict()
    sec = Section.objects.filter(active = True).order_by('headline')
    for j in sec:
        wfa = WorkFlowBlock.objects.filter(section__slug__iexact = j.slug, display_in_frontend=True).count()
        countDict[j.headline] = wfa
    return countDict


@register.filter
def get_events(request):
    domain = sub_domain(request)
    event_list = ''
    if domain == "english" or domain == "wsfdemo" or domain == 'localhost8000' or domain == "whiteswandemo":
        event_list = Event.objects.filter(active=True, language=eng_lang)
    else:
        event_list = Event.objects.filter(active=True, language__slug=str(domain))
    return event_list


@register.filter
def get_news(request):
    domain = sub_domain(request)
    news_list = ''
    if domain == "english" or domain == "wsfdemo" or domain == 'localhost8000' or domain == "whiteswandemo":
        try:
            news_list = News.objects.filter(active=True, language=eng_lang).latest('id')
        except:
            pass
    else:
        try:
            news_list = News.objects.filter(active=True, language__slug=str(domain)).latest('id')
        except:
            pass
    return news_list


@register.filter
def get_sections(request):
    domain = sub_domain(request)
    section_list = ''
    if domain == "english" or domain == "wsfdemo" or domain == 'localhost8000' or domain == "whiteswandemo":
        section_list = Section.objects.filter(active=True, display = True, language=eng_lang)
    else:
        section_list = Section.objects.filter(active=True, display = True, language__slug =str(domain))
    return section_list


@register.filter
def get_dict(request):
    workflows = WorkFlowBlock.objects.all().order_by('-created_on')
    w_dict = {}
    for i in range(workflows[0].created_on.year, workflows[len(workflows)-1].created_on.year-1, -1):
        w_dict[i] = {}
        for month in range(1,13):
            w_dict[i][month] = []
    for event in workflows:
        w_dict[event.created_on.year][event.created_on.month].append(event)
    w_sorted_keys = list(reversed(sorted(w_dict.keys())))
    list_wfs = []
    for key in w_sorted_keys:
        adict = {key:w_dict[key]}
        list_wfs.append(adict)
    return list_wfs


@register.assignment_tag
def get_weeks(month, year):
    count ={}
    weeks = []
    workflows = WorkFlowBlock.objects.filter(created_on__year=year,created_on__month=month).order_by('-created_on')
    for w in workflows:
        week_number = (w.created_on.day - 1) // 7 + 1
        weeks.append(week_number)
    for i in weeks:
        if count.has_key(i):
            count[i] += 1
        else:
            count[i] = 1
    return count

@register.filter
def to_class_name(value):
    return value.__class__.__name__


@register.assignment_tag
def get_front_menus(request):
    domain = sub_domain(request)
    if domain == "english" or domain == "wsfdemo" or domain == "localhost8000" or domain == "whiteswandemo":
        return FrontMenu.objects.filter(parent=None, active=True,language=eng_lang).order_by('listingOrder')[:6]
    else:
        return FrontMenu.objects.filter(parent=None, active=True,language__slug=str(domain)).order_by('listingOrder')[:6]


@register.assignment_tag
def get_non_display_sections(request):
    domain = sub_domain(request)
    if domain == "english" or domain == "wsfdemo" or domain == "localhost8000" or domain == "whiteswandemo":
        return Section.objects.filter(active=True, display = False, language=eng_lang)
    else:
        return Section.objects.filter(active=True, display = False, language__slug=str(domain))


@register.assignment_tag
def featured_video(request):
    domain = sub_domain(request)
    if domain == "english" or domain == "wsfdemo" or domain == "localhost8000" or domain == "whiteswandemo":
        return Videos.objects.filter(active=True, language=eng_lang).order_by('?')[:1]
    else:
        return Videos.objects.filter(active=True, language__slug=str(domain)).order_by('?')[:1]


@register.assignment_tag
def get_commic_strip(request):
    domain = sub_domain(request)
    if domain == "english" or domain == "wsfdemo" or domain == "localhost8000" or domain == "whiteswandemo":
        return Commic_Strip.objects.filter(active=True, language=eng_lang, not_display=False).order_by('?')
    else:
        return Commic_Strip.objects.filter(active=True, language__slug=str(domain), not_display=False).order_by('?')


@register.filter
def get_terms_of_use(value):
    return Our_Sections.objects.filter(active=True, featured=True, category__name='Terms-of-Use')


@register.filter
def get_cookie(request):
    return request.COOKIES.get('colorboxShown')


import random
def get_random():
    weight_list = ['6','4','7','4','5','5','6']
    return random.choice(weight_list)


@register.assignment_tag
def get_json_tags(request):
    data = []
    menus = ''
    domain = sub_domain(request)
    if domain == "english" or domain == "wsfdemo" or domain == "localhost8000" or domain == "whiteswandemo":
        menus = FrontMenu.objects.filter(parent=None, active=True, language=eng_lang).order_by('?')
        non_sections = Section.objects.filter(active=True, display = True, language=eng_lang)
    else:
        menus = FrontMenu.objects.filter(parent=None, active=True, language__slug = str(domain)).order_by('?')
        non_sections = Section.objects.filter(active=True, display = True, language__slug = str(domain))
    for i in menus:
        temp_data = {}
        temp_data['text'] = i.name.encode('utf-8')
        temp_data['weight'] = int(get_random())
        temp_data['link'] = str('/'+i.slug+'/')
        data.append(temp_data)
    for i in non_sections:
        temp_data1 = {}
        temp_data1['text'] = i.headline.encode('utf-8')
        temp_data1['weight'] = int(get_random())
        temp_data1['link'] = str('/psychiatric-disorders/'+i.slug+'/')
        data.append(temp_data1)
    return data


@register.assignment_tag
def get_home_json_tags(request):
    data = []
    menus = ''
    domain = sub_domain(request)
    if domain == "english" or domain == "wsfdemo" or domain == "localhost8000" or domain == "whiteswandemo":
        menus = FrontMenu.objects.filter(parent=None, active=True, language=eng_lang).order_by('?')[:6]
    else:
        menus = FrontMenu.objects.filter(parent=None, active=True, language__slug = str(domain)).order_by('?')[:6]
    return menus

@register.assignment_tag
def get_domain(request):
    return sub_domain(request)

@register.assignment_tag
def get_banners(request):
    domain = sub_domain(request)
    if domain == "english" or domain == "wsfdemo" or domain == "localhost8000" or domain == "whiteswandemo":
        return Our_Banners.objects.filter(category__name='Home-Page', active=True, language=eng_lang, featured=True).order_by('listing_order')
    else:
        return Our_Banners.objects.filter(category__name='Home-Page', active=True, language__slug=str(domain), featured=True).order_by('listing_order')


@register.assignment_tag
def get_user_languages(user):
    user_obj = User.objects.get(pk=user)
    languages = ''
    workflow = ''
    admin_user = ''
    try:
        workflow = WorkFlowUser.objects.get(user=user_obj)
    except:
        pass
    try:
        admin_user = Admin_User.objects.get(user=user_obj)
    except:
        pass
    if workflow and not admin_user:
        languages = workflow.language.all()
    elif admin_user and not workflow:
        languages = admin_user.language.all()
    elif admin_user and workflow:
        languages = list(set(itertools.chain([i for i in workflow.language.all()],
                              itertools.chain([i for i in admin_user.language.all()]))))
    return languages

