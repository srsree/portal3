from django.shortcuts import render
from mcms.models import *
from mcms.forms import *
from ccavenue.models import Subscription
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect,HttpResponse,Http404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage, BadHeaderError
from django.template import Context
from django.template.loader import get_template
from datetime import date, timedelta, datetime
from mcms.templatetags.front_tags import yearsago
from django.views.decorators.csrf import csrf_exempt
import uuid
from Portal.settings import ccaccess_code,ccworking_key,ccredirect_url,cccancel_url

# Create your views here.


def subscription_required(request):
    # Check that the user is Subscribed logged in.
    # This decorator ensures that the view functions it is called on can be 
    # accessed only by anonymous users. When an authenticated user accesses
    # such a protected view, they are redirected to the address specified in 
    # the field named in `next_field` or, lacking such a value, the URL in 
    today_date = datetime.datetime.now().date()
    subscribed = False
    prev_year_date = yearsago(1, today_date)
    user = request.user
    sub = ''
    if not user.is_anonymous and Editor.objects.filter(user__email=user.email):
        subscribed = True
    if not user.is_anonymous:
        sub = Subscription.objects.filter(status="Success", email=user.email, created_on__gte=prev_year_date)
    if sub:
        subscribed = True
    return subscribed


def subscription_required_new(request):
    today_date = datetime.datetime.now().date()
    subscribed = False
    prev_year_date = yearsago(1, today_date)
    user = request.user
    offlineaccess, onlineaccess = [], []
    if not user.is_anonymous():
        offlineaccess = Subscription.objects.filter(status="Success", email=user.email, created_on__gte=prev_year_date, ptype='ind-4')
        onlineaccess = Subscription.objects.filter(status="Success", email=user.email, created_on__gte=prev_year_date).exclude(ptype='ind-4')
    return {'offlineaccess':offlineaccess, 'onlineaccess':onlineaccess}

def raise_404(request):
    # to raise 404 error
    # if any error appears if data not exists
    # if url mismatch 
    # if query gives error
    # if object doest not find we can use this function
    return render(request, '404.html', {})


def raise_500(request):
    # to raise 500 error
    # if any error appears if data not exists
    # if url mismatch 
    # if server error
    # if internal server error
    return render(request, '500.html', {})

def signout(request):
    # signout function
    # logout functions  user logout function
    logout(request)
    return HttpResponseRedirect('/')

def home(request):
    # Home page function
    # photo_gallery : includes in photo features section in which all active photo feature will appears
    # columnists : is columists section which comes from Columnists models
    # banners : Home banners
    # fms : All menus dispalying after banners, in which latest story of all menu displays in home page
    # currentissue : currentissue is latest currentissue from Currentissue model
    # travel : Who dod you want to be section
    # travel_articles : 6 articles which featured = True 
    if request.session.get('nextfb'):
        next = str(request.session.get('nextfb'))
        del request.session['nextfb']
        return HttpResponseRedirect(next)
    currentissue = ''
    travel = ''
    photo_gallery = PhotoFeature.objects.filter(active=True).order_by('-id')
    columnists = Columnists.objects.filter(active=True).order_by('?')
    columnists_home = Columnists.objects.filter(active=True).exclude(col_order=None).order_by('col_order')[:4]
    banners = HomeBanners.objects.filter(active=True).order_by('listing_order')
    fms = FrontMenu.objects.filter(active=True).exclude(slug="hall-of-fame").order_by('listingOrder')[:6]
    try:
        currentissue = Currentissue.objects.filter(active=True).latest('id')
    except:
        pass
    try:
        travel = FrontMenu.objects.get(slug="hall-of-fame",active=True)
        travel_articles = travel.get_articles().filter(featured=True).order_by('listing_order')[:6] # to display in who do you want to be section
    except:
        pass
   # return render(request, 'home.html', locals())
    response = render(request, 'home.html', locals())
    # response.set_cookie("popup",'1', max_age=1200)
    return response 
    


def archive(request):
    #Archive page function
    archives = Archive.objects.filter(active=True).order_by('-date')
    return render(request, 'archive.html', locals())


def photo(request):
    # photo feature will be displayed here
    # all slideshow content will display
    photos = PhotoFeature.objects.filter(active=True).order_by('-id')
    return render(request, 'photo.html', locals())


def photo_feature(request, slug):
    # photo feature will be displayed here
    # all slideshow content will display
    photo = ''
    photos = ''
    try:
        photo = PhotoFeature.objects.get(slug=slug)
    except:
        return raise_404
    if photo:
        photos = PhotoFeatureImages.objects.filter(photo_feature=photo,active=True)
    return render(request, 'photo_detail.html', locals())

def inner(request, slug):
    #Inner page function
    menu = ''
    try:
        menu = FrontMenu.objects.get(slug=slug,active=True)
    except:
        return raise_404
    menuslug = menu.slug
    return render(request, 'inner.html', locals())

from ccavenue.views import *
def article(request, slug, aslug):
    # Article page function 
    # which includes all stories

#    if 'seen' in request.session and 'aslug' in request.session:
#        if not request.session['aslug'] == aslug:
#            return HttpResponseRedirect('/subscribe/')
#    else:
#        request.session['aslug'] = aslug
#        request.session['seen'] = 'true'

    menu, menuslug = '', ''
    comit = False
    not_subscribed = False
    s = subscription_required_new(request)
    article = ''
    article = get_object_or_404(Article, slug=aslug,active=True)
    no_perm = False
#    ctnt_obj=contentdetails_add(request)
#    cookie_obj=contentdetail_sql(request)
    if s['offlineaccess'] and not s['onlineaccess'] and article.subscriber_only:
        no_perm = True
    try:
        del request.session['nextfb']
    except:
        pass
    try:
        menu = FrontMenu.objects.get(slug=slug,active=True)
        menuslug = menu.slug
    except:
        return raise_404
    if article and article.subscriber_only and not subscription_required(request):
        #return HttpResponseRedirect('/subscribe/')
        not_subscribed = True
        merchant_id = 20756
        oid = uuid.uuid4()
        order_id = str(oid)[:30]
        access_code = ccaccess_code #"AVZC00BA44CA22CZAC"
        working_key = ccworking_key #"2AF08497DFEDB4424306C27C0BFE5102"
        test_url = "https://test.ccavenue.com"
        production_url = "https://secure.ccavenue.com"
        currency = "INR"
        language ="en"
        redirect_url = ccredirect_url #"http://www.civilsocietyonline.com/subscribe/redirect/"
        cancel_url = cccancel_url #"http://www.civilsocietyonline.com/subscribe/redirect/"
    form = CommentForm()
    if request.method == "POST" and not not_subscribed:
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            img = request.FILES.get('image')
            f = form.save(commit=False)
            f.content_type = ContentType.objects.get_for_model(article)
            f.object_id = str(article.id)
            f.image = img
            f.save()
            comit = True
    if request.method == 'POST' and not_subscribed:
        p_merchant_id = request.POST.get('merchant_id')
        p_order_id = request.POST.get('order_id')
        p_currency = request.POST.get('currency')
        amount = request.POST.get('amount')
        profession = request.POST.get('profession')
        p_amount = str(converted_amounts[amount])
        year = 1
        p_redirect_url = request.POST.get('redirect_url')
        p_cancel_url = request.POST.get('cancel_url')
        p_language = request.POST.get('language')
        p_billing_name = request.POST.get('billing_name')
        p_billing_address = request.POST.get('billing_address')
        p_billing_city = request.POST.get('billing_city')
        p_billing_state = request.POST.get('billing_state')
        p_billing_zip = request.POST.get('billing_zip')
        cnt = Country.objects.get(id = request.POST.get('billing_country'))
        p_billing_country = cnt.name
        p_billing_tel = request.POST.get('billing_tel')
        p_billing_email = request.POST.get('billing_email')
        Subscription.objects.create(name = p_billing_name, amount=p_amount, year = year, orderid=p_order_id, status="Pending", 
                                   email =p_billing_email, phone = p_billing_tel, address = p_billing_address, 
                                   city = p_billing_city, state = p_billing_state, country = cnt, pincode= p_billing_zip)
        merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_billing_name+'&'+'delivery_address='+p_billing_address+'&'+'delivery_city='+p_billing_city+'&'+'delivery_state='+p_billing_state+'&'+'delivery_zip='+p_billing_zip+'&'+'delivery_country='+p_billing_country+'&'+'delivery_tel='+p_billing_tel+'&'
        encryption = encrypt(merchant_data,working_key)
        return render(request, 'payment.html', locals())
    return render(request, 'article.html', locals())

def gallery(request):
    # gallery page function
    # /gallery/ page displaying all gallery categories
    menuslug = 'gallery'
    gals = Gallery.objects.filter(active=True)
    return render(request, 'gallery.html', locals())

def more(request):
    # More page function
    # excluding all menus which menus are displaying in top header
    # in which all menus all will be displayed including top menus
    menuslug = 'more'
    fmenus = FrontMenu.objects.filter(active=True).order_by('listingOrder')[5:]
    return render(request, 'more.html', locals())

import watson
def search(request):
    # Search page function
    # by using watson app we are searching here
    # register all modules using watson.register(Module)
    # it uses mysql free text search method, all data will be stored in json format
    q = request.GET.get('q')
    results = watson.search(q,models=(FrontMenu.objects.filter(active=True),
                                        Article.objects.filter(active=True)))
    return render(request, 'search.html', locals())

@login_required(login_url='/login/')
def subscribe(request):
    # ubscribe function
    # subscribe to read to articles,
    # if user is not subscribed, we are not allowing to read the articles,
    # subscribe will be yearly, monthly based subscription
    return render(request, 'subscribe.html', locals())

def about_us(request):
    # about us page
    about = AboutUs.objects.all()
    menuslug = "about-us"
    return render(request, 'about.html', locals())

from django.shortcuts import *

def column(request, slug):
    # column detail page
    # based on slug filtering column
    columns = get_object_or_404(ColumnCategory , slug=slug)
    return render(request, 'column.html', locals())

def columns(request):
    # column detail page
    # based on slug filtering column
    columns = Columns.objects.filter(active=True).order_by("-created_on")[:100]
    return render(request, 'columns.html', locals())

def column_detail(request, cslug, slug):
    # import ipdb;ipdb.set_trace()
    comit  = request.GET.get('comment')
    category = get_object_or_404(ColumnCategory , slug=cslug)
    column = get_object_or_404(Columns , slug=slug)
    form = CommentForm()
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            img = request.FILES.get('image')
            f = form.save(commit=False)
            f.content_type = ContentType.objects.get_for_model(column)
            f.object_id = str(column.id)
            f.image = img
            f.save()
            comit = True
            return HttpResponseRedirect('/column/'+cslug+"/"+slug+"/"+"?comment=True")
    return render(request, 'column_detail.html', locals())


def frontend_login(request):
    #Front End login Function
    next = request.GET.get('next')
    request.session['nextfb'] = next
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if next:
        redirect_url = next
    else:
        redirect_url = '/'
    if request.method == 'POST':
        form = request.POST.get('form')
        first_name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if form == 'signup':
            check = User.objects.filter(email=email)
            if not check:
                user_obj = User.objects.create_user(email, email, password)
                user_obj.first_name = first_name
                user_obj.save()
                template = get_template('register_email.html')
                subject = "Thank You For Registering With Portal"
                context = Context({'username':email,'password':password})
                content = template.render(context)
                sender_mail = "subscriptions@civilsocietyonline.com"
                email5 = EmailMessage(subject, content, sender_mail,[email,],headers = {'Reply-To': sender_mail})
                email5.content_subtype = "html"
                email5.send()
                msg = "User Created Successfully. Please login with same email and password"
                user1 = authenticate(username=email, password=password)
                login(request, user1)
                return HttpResponseRedirect(redirect_url)
            else:
                msg = "You have been registered already please login with your that username and password"
        elif form == 'login':
            user = authenticate(username=request.POST['email'], password=request.POST['password'])
            if user is not None:
                login(request, user)
                if not UserPasswordChange.objects.filter(user=user):
                    return HttpResponseRedirect('/change-password/')
                else:
                    return HttpResponseRedirect(redirect_url)
            else:
                msg = "Invalid Username and Password"
    return render(request, 'login.html', locals())


@login_required(login_url="/login/")
def password_change(request):
    if request.method == "POST":
        password = request.POST.get('password')
        user = request.user
        user.set_password(password)
        user.save()
        UserPasswordChange.objects.create(user = user)
        return render(request, 'password_change_done.html', locals())
    return render(request, 'password_change.html', locals())


def newsletter(request):
    # News Letter Function
    newsletters = NewsLetter.objects.all()
    if request.method == 'POST':
        email = request.POST.get('email')
        subscribe_obj = Subscribe.objects.create(email=email)
        subscribed = True
        template = get_template('newsletter_email.html')
        subject = "Thank you for signing up for Civil Society newsletters"
        context = Context()
        content = template.render(context)
        sender_mail = "subscriptions@civilsocietyonline.com"
        email5 = EmailMessage(subject, content, sender_mail,[email,'response@civilsocietyonline.com','umesh@civilsocietyonline.com',],headers = {'Reply-To': sender_mail})
        email5.content_subtype = "html"
        email5.send()
    return render(request, 'newsletter.html', locals())

@csrf_exempt
def write_to_us(request):
    # function to display write to us page
    # post method to get the content form user who are written to editor
    # will save to WriteToUs table
    # based on this form submit will send an alert to users and superuser
    menuslug = "write-to-us"
    form = WriteToUsForm()
    if request.method == "POST":
        form = WriteToUsForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save(commit=False)
            f.save()
            subject = "A New Enquiry on site."
            template = get_template('write_to_us_email.html')
            context = Context({'form': f})
            content = template.render(context)
            sender_mail = "subscriptions@civilsocietyonline.com"
            email5 = EmailMessage(subject, content, sender_mail,['response@civilsocietyonline.com','umesh@civilsocietyonline.com','rita@civilsocietyonline.com',],headers = {'Reply-To': sender_mail})
            email5.content_subtype = "html"
            email5.send()
            comit = True
    return render(request, 'writetous.html', locals())


from django.template.response import TemplateResponse
from django.contrib.sites.models import RequestSite
from itertools import chain
import datetime

def sitemap(request, template_name='sitemap1.xml', content_type='application/xml',
            mimetype=None):
    urls = []
    articles = Article.objects.filter(active=True, frontmenu__active=True)
    columncategory = ColumnCategory.objects.filter(active=True)
    columns = Columns.objects.filter(active=True)
    frontmenus = FrontMenu.objects.filter(active=True)
    photofeatures = PhotoFeature.objects.filter(active=True)
    protocol = "http"
    maindomain = RequestSite(request).domain
    main = protocol+"://"+maindomain
    main_url_info = {
            'location':main,
            'lastmod':datetime.datetime.now(),
            'changefreq':"weekly",
            'priority':"1.0",
        }
    urls.append(main_url_info)
    about = protocol+"://"+maindomain+ "/about-us/"
    about_url_info = {
            'location':about,
            'lastmod':datetime.datetime.now(),
            'changefreq':"weekly",
            'priority':"1.0",
        }
    urls.append(about_url_info)
    gallery = protocol+"://"+maindomain+ "/gallery/"
    gallery_url_info = {
            'location':gallery,
            'lastmod':datetime.datetime.now(),
            'changefreq':"weekly",
            'priority':"1.0",
        }
    urls.append(gallery_url_info)
    archive = protocol+"://"+maindomain+ "/archive/"
    archive_url_info = {
            'location':archive,
            'lastmod':datetime.datetime.now(),
            'changefreq':"weekly",
            'priority':"1.0",
        }
    urls.append(archive_url_info)
    write_to_us = protocol+"://"+maindomain+ "/write-to-us/"
    write_to_us_url_info = {
            'location':write_to_us,
            'lastmod':datetime.datetime.now(),
            'changefreq':"weekly",
            'priority':"1.0",
        }
    urls.append(write_to_us_url_info)
    for i in frontmenus:
        loc = protocol+"://"+maindomain+ "/" + i.slug + "/"
        url_info = {
            'location':loc,
            'lastmod':datetime.datetime.now(),
            'changefreq':"weekly",
            'priority':"1.0",
        }
        urls.append(url_info)
    for i in articles:
        loc = protocol+"://"+maindomain+i.get_absolute_url()
        url_info = {
            'location':loc,
            'lastmod':datetime.datetime.now(),
            'changefreq':"weekly",
            'priority':"1.0",
        }
        urls.append(url_info)
    for i in columncategory:
        loc = protocol+"://"+maindomain+ "/column/" + i.slug + "/"
        url_info = {
            'location':loc,
            'lastmod':datetime.datetime.now(),
            'changefreq':"weekly",
            'priority':"1.0",
        }
        urls.append(url_info)
    for i in columns:
        loc = protocol+"://"+maindomain+ "/column/"+ i.columnist.category.slug + "/" + i.slug + "/"
        url_info = {
            'location':loc,
            'lastmod':datetime.datetime.now(),
            'changefreq':"weekly",
            'priority':"1.0",
        }
        urls.append(url_info)
    photo = protocol+"://"+maindomain+ "/photo-feature/"
    photo_url_info = {
            'location':photo,
            'lastmod':datetime.datetime.now(),
            'changefreq':"weekly",
            'priority':"1.0",
        }
    urls.append(photo_url_info)
    for i in photofeatures:
        loc = protocol+"://"+maindomain+ "/photo-feature/"+ i.slug + "/"
        url_info = {
            'location':loc,
            'lastmod':datetime.datetime.now(),
            'changefreq':"weekly",
            'priority':"1.0",
        }
        urls.append(url_info)
    return TemplateResponse(request, template_name, {'urlset': urls},
                            content_type=content_type)

from django.db import connection

def contentdetail_sql(request):
    cursor = connection.cursor()
    obj=request.META['CSRF_COOKIE']
    cursor.execute("SELECT count_value FROM mcms_contentdetails WHERE cookie = %s",[obj])
    row_val =cursor.fetchone()
    row_value=row_val[0]
    return row_value


def contentdetails_add(request):
    cursor = connection.cursor()
    cobj=request.META['CSRF_COOKIE']
    content_type=ContentType.objects.get(model__iexact='article')
    ct_id=content_type.id
    row=cursor.execute("SELECT count_value FROM mcms_contentdetails WHERE cookie = %s ",[cobj])
    if row:
        ct_obj=cursor.execute("UPDATE mcms_contentdetails SET count_value = count_value+1 WHERE cookie=%s",[cobj])
    else:
        ct_obj=cursor.execute("INSERT INTO mcms_contentdetails (created_on,modified_on,active,cookie,count_value,content_type,object_id) VALUES(now(), now(), %s ,%s, %s, %s, %s)",[int(1),cobj,int(1),content_type,int(ct_id)])
    return ct_obj

