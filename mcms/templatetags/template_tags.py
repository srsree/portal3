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

from datetime import date, timedelta
from common_function import sub_domain
import itertools
from faq.models import *

register = template.Library()
eng_lang = Language.objects.get(name="English")

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
    #event_list = Event.objects.filter(start_date__lte=(datetime.datetime.today()+datetime.timedelta(days=1)), end_date__gte=datetime.datetime.today())
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
    #news_list = News.objects.filter(start_date__lte=(datetime.datetime.today()+datetime.timedelta(days=1)), end_date__gte=datetime.datetime.today())
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


'''@register.filter
def get_dict(request):
    years = []
    year_dict = {}
    month_dict = {}
    week_dict = {}
    workflows = WorkFlowBlock.objects.all().order_by('-created_on')
    wdates = WorkFlowBlock.objects.dates('created_on', 'year', order='DESC')
    import pdb;pdb.set_trace()
    for wf in wdates:
        years.append(wf.year)
    yrs = list(set(years))
    for i in yrs:
        temp_month = []
        print "iiiiiiiiiiiiiiii", i
        months = workflows.filter(created_on.year = int(i))
        for j in months:
            temp_month.append(j.created_on.month)
        year_dict[i] = temp_month
        print "temp month-----",temp_month
    print "temp year-----",year_dict
    return None'''

@register.filter
def get_dict(request):
    #create a dict with the years and months:events 
    workflows = WorkFlowBlock.objects.all().order_by('-created_on')
    w_dict = {}
    for i in range(workflows[0].created_on.year, workflows[len(workflows)-1].created_on.year-1, -1):
        w_dict[i] = {}
        for month in range(1,13):
            w_dict[i][month] = []
    for event in workflows:
        w_dict[event.created_on.year][event.created_on.month].append(event)
    #this is necessary for the years to be sorted
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
        #temp_data.replace('')
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
    '''for i in menus:
        temp_data = {}
        temp_data['text'] = i.name.encode('utf-8')
        temp_data['weight'] = int(get_random())
        ct = ContentType.objects.get_for_model(i)
        temp_data['link'] = "javascript:funcname("+str(ct.id)+", "+str(i.id)+")"
        data.append(temp_data)'''
    return menus


@register.assignment_tag
def get_default_main_tags(request):
    domain = sub_domain(request)
    non_sections = ''
    if domain == "english" or domain == "wsfdemo" or domain == 'localhost8000' or domain == "whiteswandemo":
        non_sections = Section.objects.filter(active=True, display = True, language=eng_lang)
    else:
        non_sections = Section.objects.filter(active=True, display = True, language__slug =str(domain))
    data = []
    for i in non_sections:
        temp_data = {}
        temp_data['text'] = i.headline.encode('utf-8')
        temp_data['weight'] = int(get_random())
        temp_data['link'] = str('/psychiatric-disorders/'+i.slug+'/')
        data.append(temp_data)
    t1 = {'text':'Depression','weight':int(get_random()),'link':'/psychiatric-disorders/depression/'}
    t2 = {'text':'Bipolar Disorder','weight':int(get_random()),'link':'/psychiatric-disorders/depression/bipolar-disorder/'}
    t3 = {'text':'Obsessive Compulsive Disorder','weight':int(get_random()),'link':'/psychiatric-disorders/anxiety/obsessive-compulsive-disorder-ocd/'}
    t4 = {'text':'Dementia','weight':int(get_random()),'link':'/psychiatric-disorders/geriatric-disorders/dementia/'}
    t5 = {'text':"Alzheimer's Disease",'weight':int(get_random()),'link':'/psychiatric-disorders/geriatric-disorders/alzheimers-disease/'}
    t6 = {'text':'Speech Disorders','weight':int(get_random()),'link':'/psychiatric-disorders/childhood-disorders/speech-disorder/'}
    t7 = {'text':'Autism','weight':int(get_random()),'link':'/psychiatric-disorders/childhood-disorders/autism/'}
    t8 = {'text':'ADHD','weight':int(get_random()),'link':'/psychiatric-disorders/childhood-disorders/attention-deficit-hyperactivity-disorder-adhd/'}
    t9 = {'text':'PTSD','weight':int(get_random()),'link':'/psychiatric-disorders/anxiety/post-traumatic-stress-disorder-ptsd/'}
    t10 = {'text':'Phobias','weight':int(get_random()),'link':'/psychiatric-disorders/anxiety/phobias/'}
    t11 = {'text':'Social Anxiety Disorder','weight':int(get_random()),'link':'/psychiatric-disorders/anxiety/social-anxiety-disorder-sad/'}
    data.append(t1)
    data.append(t2)
    data.append(t3)
    data.append(t4)
    data.append(t5)
    data.append(t6)
    data.append(t7)
    data.append(t8)
    data.append(t9)
    data.append(t10)
    data.append(t11)
    return data


kannada_dict = {'between':'ಕಪ್ಪು ಬಿಳುಪಿನ ಮಧ್ಯೆ','about-us':'ನಮ್ಮ ಬಗ್ಗೆ','who-we-are':'ನಮ್ಮ ಪರಿಚಯ','the-team':'ನಮ್ಮ ತಂಡ','our-partners':'ನಮ್ಮ ಜೊತೆಗಾರರು', 
'terms':'ಬಳಕೆಯ ಷರತ್ತುಗಳು','also-read':'ಇನ್ನೂ ಓದಿ','home':'ಮುಖಪುಟ','read-more':'ಇನ್ನೂ ಓದಿ','view-more':'ಇನ್ನೂ ಓದಿ','know-more':'ಹೆಚ್ಚಿನ ವಿವರ','featured-columns':'ವಿಶೇಷ ಅಂಕಣಗಳು','videos':'ಚಿತ್ರೀಕರಣ ಮಾಲಿಕೆ','explore':'ಹೆಚ್ಚಿನ ಮಾಹಿತಿ','search':'ಹುಡುಕು','featured-video':'ವಿಶೇಷ ಚಿತ್ರೀಕರಣ ಮಾಲಿಕೆ', 'whiteswanfoundation':'ವೈಟ್ ಸ್ವಾನ್ ಫೌಂಡೇಶನ್','related':'ಇತರ','board_of_advisors':'ಸಲಹೆಗಾರರ ಮಂಡಳಿ','board_of_directors':'ನಿರ್ದೇಶಕರ ಮಂಡಳಿ','our-editorial-policy':'ನಮ್ಮ ಸಂಪಾದಕೀಯ ನೀತಿ', 'featured':'ವಿಶೇಷ ಲೇಖನಗಳು', 'columns':'ಅಂಕಣ', 'events':'ವಿಶೇಷ ಕಾರ್ಯಕ್ರಮಗಳು', 'news':'ಸುದ್ಧಿ ಸಮಾಚಾರ', 'understandingmentalhealth':'ಮಾನಸಿಕ ಆರೋಗ್ಯದ ಗ್ರಹಿಕೆ', 'connect':'ನಮ್ಮನ್ನು ಸಂಪರ್ಕಿಸಿ', 'benefit':'ಈ ಮಾಹಿತಿಯನ್ನು ನೀವು ಹೇಗೆ ಉಪಯೋಗಿಸಬಹುದು','all-results':'ಸಮಗ್ರ ಲೇಖನಗಳು', 'disorders':'ಮಾನಸಿಕ ಖಾಯಿಲೆಗಳು', 'articles':'ಲೇಖನಗಳು', 'experts-speak':'ತಜ್ಞರ ಲೇಖನಗಳು', 'myths-facts':'ವಾಸ್ತವ ಹಾಗು ಕಲ್ಪನೆಗಳು', 'partners':'ಜೊತೆಗಾರರು', 'other-results':'ಇತರ ಲೇಖನಗಳು','expert-columns':'ತಜ್ಞರ ಲೇಖನಗಳು','interviews':'ಸಂದರ್ಶನ','case-study':'ಕೇಸ್ ಸ್ಟಡೀ','careers':'ಉದ್ಯೋಗ', 'hiring':'ವೈಟ್ ಸ್ವಾನ್  ಫೌಂಡೇಶನ್ ನಲ್ಲಿ ಉದ್ಯೋಗ ಲಭ್ಯ','role':'ಕೆಲಸ','job-location':'ಕೆಲಸದ ಸ್ಥಳ'}

bengali_dict = {'between':'সাদা কালোর মাঝামাঝি','about-us':'আমাদের পরিচয়','who-we-are':'কে আমরা ','the-team':'আমাদের সদস্যরা ','our-partners':'আমাদের সহযোগী', 'terms':'নিয়মাবলী','also-read':'আরও পড়ুন ','home':'হোম ','read-more':'আরও পড়ুন ','view-more':'আরও দেখুন ','know-more':'বিশদে জানুন ','featured-columns':'বিশিষ্ট প্রবন্ধ ','videos':'ভিডিও','explore':'অনুসন্ধান করুন ','search':'খোঁজ','featured-video':'বিশিষ্ট ভিডিও', 'whiteswanfoundation':'হোয়াইট সোয়ান ফাউন্ডেশন ','related':'সম্পর্কিত','board_of_advisors':'উপদেষ্টা মণ্ডলী ','board_of_directors':'পরিচালক পরিষদ','our-editorial-policy':'সম্পাদকীয় নীতি ', 'featured':'বিশিষ্ট প্রবন্ধ ', 'columns':'বিশেষজ্ঞের কলমে ', 'events':'অনুষ্ঠান', 'news':'খবর', 'understandingmentalhealth':'মানসিক স্বাস্থ্যকে বোঝা ', 'connect':'যোগাযোগ করুন', 'benefit':'উপকার','all-results':'সমস্ত ফলাফল', 'disorders':'বিকার', 'articles':'প্রবন্ধ ', 'experts-speak':'বিশেষজ্ঞের মতামত', 'myths-facts':'ধারনা এবং বাস্তব', 'partners':'আমাদের সহযোগী', 'other-results':'অন্যান্য ফলাফল','expert-columns':'বিশেষজ্ঞের কলমে', 'interviews':'সাক্ষাতকার', 'case-study':'কেস স্টাডি'}

hindi_dict = {'between':'श्वेत और श्याम','about-us':'हमारे बारे में','who-we-are':'हमारे बारे में ','the-team':'टीम','our-partners':'हमारे सहयोगी', 'terms':'नियम और शर्तें','also-read':'और पढ़े ','home':'होम','read-more':'आगे पढ़ें ','view-more':'और देखें','know-more':'और जानें ','featured-columns':'विशेष लेखन','videos':'वीडियो','explore':'और जानकारी','search':'खोज','featured-video':'फ़ीचर वीडियो', 'whiteswanfoundation':'वाइट  स्वान फ़ाउंडेशन','related':'संबंधित','board_of_advisors':'सलाहकार बोर्ड ','board_of_directors':'निदेशक बोर्ड','our-editorial-policy':'हमारी संपादकीय नीति', 'featured':'विशेष लेखन', 'columns':'विचार धारा', 'events':'घटनाएं', 'news':'समाचार', 'understandingmentalhealth':'मानसिक सेहत को समझें', 'connect':'हमसे जुड़ें', 'benefit':'इस पोर्टल से फ़ायदा','all-results':'सभी परिणाम', 'disorders':'रोग', 'articles':'लेखन ', 'experts-speak':'विशेषज्ञ राय', 'myths-facts':'मिथक और सथ्य', 'partners':'हमारे सहयोगी', 'other-results':'अन्य परिणाम','expert-columns':'विशेषज्ञ लेखन', 'interviews':'बातचीत', 'case-study':'विषय की अध्ययन'}


@register.assignment_tag
def get_kannada_clouds(request):
    domain = sub_domain(request)
    a = []
    if domain == "kannada":
        a = [125, 126, 128, 132, 138, 141, 152, 153, 154, 156, 158, 160]
    elif domain == "bengali":
        a = [171, 216, 217, 209, 173, 180, 172, 194, 218, 197, 208, 214]
    data = WorkFlowBlock.objects.filter(id__in=a).order_by('?')[:10]
    return data


@register.assignment_tag
def get_lang_word(wrd,lang):
    if lang == "kannada":
        if kannada_dict[wrd]:
            return kannada_dict[wrd]
        else:
            return None
    elif lang == "bengali":
        if bengali_dict[wrd]:
            return bengali_dict[wrd]
        else:
            return None
    elif lang == "hindi":
        if hindi_dict[wrd]:
            return hindi_dict[wrd]
        else:
            return None
    else:
        return None

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

@register.filter
def get_manage_front_menus(request):
    frontmenu = []
    lang = request.session.get('lang')
    if not lang:
        wlist = WorkFlowBlock.objects.filter(active=True)
        artlist = Article.objects.filter(active=True)
        faqlist = FAQ_Category.objects.filter(is_active=True)
    else:
        wlist = WorkFlowBlock.objects.filter(language__slug=lang, active=True)
        artlist = Article.objects.filter(language__slug=lang, active=True)
        faqlist = FAQ_Category.objects.filter(language__slug=lang, is_active=True)
    if wlist:
        frontmenu = [i.frontmenu for i in wlist]
        for i in wlist:
            if i.frontmenu:
                frontmenu.append(i.frontmenu)
    if artlist:
        for i in artlist:
            if i.frontmenu:
                frontmenu.append(i.frontmenu)
    if faqlist:
        for i in faqlist:
            if i.frontmenu:
                frontmenu.append(i.frontmenu)
    return list(set(frontmenu))


@register.assignment_tag
def get_menus_art_count(request, publish='', menuid=''):
    user = request.user
    workflow_list = []
    article_list = []
    faq_list = []
    item_list = []
    d = {}
    menu_obj = FrontMenu.objects.get(id=menuid)
    workflow_list = WorkFlowBlock.objects.filter(frontmenu__id=menu_obj.id)
    article_list = Article.objects.filter(frontmenu__id=menu_obj.id)
    faq_list = FAQ_Category.objects.filter(frontmenu__id=menu_obj.id)
    if publish == 'True':
        workflow_list = workflow_list.filter(display_in_frontend=True, doc_type='organization-idea')
        article_list = article_list.filter(display_in_frontend=True, doc_type='organization-idea')
        faq_list = faq_list.filter(display_in_frontend=True, doc_type='organization-idea')
        item_list = list(set(itertools.chain([i for i in workflow_list if i.get_workflow_state().state.name=="Published"],
                              itertools.chain([i for i in article_list if i.get_workflow_state().state.name=="Published"],
                              itertools.chain([i for i in faq_list if i.get_workflow_state().state.name=="Published"])))))
    elif publish == 'portal':
        workflow_list = workflow_list.filter(display_in_frontend=False, doc_type='organization-idea')
        article_list = article_list.filter(display_in_frontend=False, doc_type='organization-idea')
        faq_list = faq_list.filter(display_in_frontend=False, doc_type='organization-idea')
        item_list = list(set(itertools.chain([i for i in workflow_list if i.get_workflow_state().state.name=="Published"],
                              itertools.chain([i for i in article_list if i.get_workflow_state().state.name=="Published"],
                              itertools.chain([i for i in faq_list if i.get_workflow_state().state.name=="Published"])))))
    elif publish == 'inprocess':
        workflow_list = workflow_list.filter(display_in_frontend=False, doc_type='organization-idea')
        article_list = article_list.filter(display_in_frontend=False, doc_type='organization-idea')
        faq_list = faq_list.filter(display_in_frontend=False, doc_type='organization-idea')
        item_list = list(set(itertools.chain([i for i in workflow_list if i.get_workflow_state().state.name!="Published"],
                                  itertools.chain([i for i in article_list if i.get_workflow_state().state.name!="Published"],
                                  itertools.chain([i for i in faq_list if i.get_workflow_state().state.name!="Published"])))))
    elif publish == 'nonsubmitted':
        workflow_list = workflow_list.filter(display_in_frontend=False, doc_type='idea')
        article_list = article_list.filter(display_in_frontend=False, doc_type='idea')
        faq_list = faq_list.filter(display_in_frontend=False, doc_type='idea')
        item_list = list(set(itertools.chain([i for i in workflow_list if i.get_workflow_state().created_by==user if not i.get_submitted_document()],
                              itertools.chain([i for i in article_list if i.get_workflow_state().created_by==user if not i.get_submitted_document()],
                              itertools.chain([i for i in faq_list if i.get_workflow_state().created_by==user if not i.get_submitted_document()])))))
    elif publish == 'submitted':
        workflow_list = workflow_list.filter(display_in_frontend=False, doc_type='idea')
        article_list = article_list.filter(display_in_frontend=False, doc_type='idea')
        faq_list = faq_list.filter(display_in_frontend=False, doc_type='idea')
        item_list = list(set(itertools.chain([i for i in workflow_list if i.get_workflow_state().created_by==user if i.get_submitted_document()],
                              itertools.chain([i for i in article_list if i.get_workflow_state().created_by==user if i.get_submitted_document()],
                              itertools.chain([i for i in faq_list if i.get_workflow_state().created_by==user if i.get_submitted_document()])))))
    elif publish == 'submitteddocuments':
        workflow_list = workflow_list.filter(display_in_frontend=False, doc_type='idea')
        article_list = article_list.filter(display_in_frontend=False, doc_type='idea')
        faq_list = faq_list.filter(display_in_frontend=False, doc_type='idea')
        item_list = list(set(itertools.chain([i for i in workflow_list if i.get_submitted_document() if i.get_workflow_state().created_by!=user],
                              itertools.chain([i for i in article_list if i.get_submitted_document() if i.get_workflow_state().created_by!=user],
                              itertools.chain([i for i in faq_list if i.get_submitted_document() if i.get_workflow_state().created_by!=user])))))
    return len(item_list)

@register.assignment_tag
def get_block_for_menu(request, publish='', menuid=''):
    user = request.user
    menu_obj = FrontMenu.objects.get(id=int(menuid))
    workflow_list = WorkFlowBlock.objects.filter(frontmenu__id=int(menuid))
    article_list = Article.objects.filter(frontmenu__id=int(menuid))
    faq_list = FAQ_Category.objects.filter(frontmenu__id=int(menuid))
    if publish == 'True':
        workflow_list = workflow_list.filter(display_in_frontend=True, doc_type='organization-idea')
        article_list = article_list.filter(display_in_frontend=True, doc_type='organization-idea')
        faq_list = faq_list.filter(display_in_frontend=True, doc_type='organization-idea')
        workflow_list = [i for i in workflow_list if i.get_workflow_state().state.name=="Published"]
        article_list = [i for i in article_list if i.get_workflow_state().state.name=="Published"]
        faq_list = [i for i in faq_list if i.get_workflow_state().state.name=="Published"]
    elif publish == 'portal':
        workflow_list = workflow_list.filter(display_in_frontend=False, doc_type='organization-idea')
        article_list = article_list.filter(display_in_frontend=False, doc_type='organization-idea')
        faq_list = faq_list.filter(display_in_frontend=False, doc_type='organization-idea')
        workflow_list = [i for i in workflow_list if i.get_workflow_state().state.name=="Published"]
        article_list = [i for i in article_list if i.get_workflow_state().state.name=="Published"]
        faq_list = [i for i in faq_list if i.get_workflow_state().state.name=="Published"]
    elif publish == 'inprocess':
        workflow_list = workflow_list.filter(display_in_frontend=False, doc_type='organization-idea')
        article_list = article_list.filter(display_in_frontend=False, doc_type='organization-idea')
        faq_list = faq_list.filter(display_in_frontend=False, doc_type='organization-idea')
        workflow_list = [i for i in workflow_list if i.get_workflow_state().state.name!="Published"]
        article_list = [i for i in article_list if i.get_workflow_state().state.name!="Published"]
        faq_list = [i for i in faq_list if i.get_workflow_state().state.name!="Published"]
    elif publish == 'submitted':
        workflow_list = workflow_list.filter(doc_type='idea')
        article_list = article_list.filter(doc_type='idea')
        faq_list = faq_list.filter(doc_type='idea')
        workflow_list = [i for i in workflow_list if i.get_workflow_state().created_by==user if i.get_submitted_document()]
        article_list = [i for i in article_list if i.get_workflow_state().created_by==user if i.get_submitted_document()]
        faq_list = [i for i in faq_list if i.get_workflow_state().created_by==user if i.get_submitted_document()]
    elif publish == 'nonsubmitted':
        workflow_list = workflow_list.filter(display_in_frontend=False, doc_type='idea')
        article_list = article_list.filter(display_in_frontend=False, doc_type='idea')
        faq_list = faq_list.filter(display_in_frontend=False, doc_type='idea')
        workflow_list = [i for i in workflow_list if i.get_workflow_state().created_by!=user]
        article_list = [i for i in article_list if i.get_workflow_state().created_by!=user]
        faq_list = [i for i in faq_list if i.get_workflow_state().created_by!=user]
    elif publish == 'submitteddocuments':
        workflow_list = workflow_list.filter(display_in_frontend=False, doc_type='idea')
        article_list = article_list.filter(display_in_frontend=False, doc_type='idea')
        faq_list = faq_list.filter(display_in_frontend=False, doc_type='idea')
        workflow_list = [i for i in workflow_list if i.get_submitted_document() if i.get_workflow_state().created_by==user if not i.get_submitted_document()]
        article_list = [i for i in article_list if i.get_submitted_document() if i.get_workflow_state().created_by==user if not i.get_submitted_document()]
        faq_list = [i for i in faq_list if i.get_submitted_document() if i.get_workflow_state().created_by==user if not i.get_submitted_document()]
    d = {'disorder':workflow_list, 'article':article_list, 'faq':faq_list}
    return d

@register.assignment_tag
def get_document_user(request, document, model_name):
    model_name = eval(model_name)
    obj = document.get_assigner()
    if obj:
        return obj.assigned_user.username
    else:
        return None
