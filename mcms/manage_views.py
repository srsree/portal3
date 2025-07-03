# manage views for CMS backend
# all functionalities related to backend stays here
from django.shortcuts import render_to_response, get_object_or_404,render
from django.utils.encoding import smart_str, smart_unicode
from django.contrib.auth.models import *
from django.contrib.auth import authenticate, login, logout
from django.template import Context, loader,RequestContext
from django.http import HttpResponseRedirect,HttpResponse,Http404
from django.template.defaultfilters import slugify
from datetime import *
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage, BadHeaderError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import password_reset
from mcms.models import *
from faq.models import *
from django.forms.models import modelform_factory
from mcms.forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.contenttypes.models import ContentType
import csv
import json
from django.template.loader import get_template
import itertools
from ccavenue.models import Subscription
from collections import defaultdict


def get_session_lang(request):
    # getting language through session
    # on select of language we are setting language to session
    # here we setting language in session and retrieving user based language
    result={}
    if request.is_ajax():
        id=request.GET.get("id")
        request.session['lang'] = id
    return HttpResponse(json.dumps(result), mimetype="application/json")


limit=20


def invalid_user(request):
    # invalid user function
    return render(request, 'invalid_user.html', locals()) 


def has_changed(instance, field):
    # common method to check the field has changed or not.
    if not instance.pk:
        return False
    old_value = instance.__class__._default_manager.\
        filter(pk=instance.pk).values(field).get()[field]
    return not getattr(instance, field) == old_value

def userid():
    # getting unique ID to generate unique id for every objects
    return uuid4().hex


def model_has_field(model_class, field_name):
    # checking the model has the filed
    # model_class : models name
    # field_name : field to be check
    return field_name in model_class._meta.get_all_field_names()

def add_form(request):
    # common add function for model form, its very usefull for all models
    # 3 parameters we need to send t work this function
    # model : Model using to "add"
    # Key = Whether to "add" or "edit"
    check = ''
    modelname = request.GET.get('model')
    key = request.GET.get('key')
    lang = request.session.get('lang')
    if lang:
        language = Language.objects.get(slug='english')
    formname = request.GET.get('form')
    if formname:
        form = eval(formname)
    else:
        form = modelform_factory(eval(modelname), exclude=('active',))
    if request.method == 'POST':
        form = form(request.POST, request.FILES)
        if model_has_field(eval(modelname), 'slug'):
            check = eval(modelname).objects.filter(slug=slugify(request.POST.get('name')))
        elif model_has_field(eval(modelname), 'name'):
            check = eval(modelname).objects.filter(name=request.POST.get('name'))
        if form.is_valid() and not check:
            f = form.save(commit=False)
            if model_has_field(eval(modelname), 'slug'):
                f.slug = slugify(request.POST.get('name'))
            f.save()
            added = True
            return HttpResponseRedirect('/manage/?key='+key)
        else:
            error = "Name Already exists or Invalid Form"
    return render_to_response('manage/add-form.html', locals(), context_instance=RequestContext(request))


def edit_form(request):
    # common edit function for model form, its very usefull for all models
    # 4 parameters we need to send t work this function
    # model : Model using to "add"
    # Key = Whether to "add" or "edit"
    # objid = object id of instance to edit
    edit = True
    check = ''
    modelname = request.GET.get('model')
    objid = request.GET.get('objid')
    formname = request.GET.get('form')
    key = request.GET.get('key')
    obj = eval(modelname).objects.get(id=objid)
    if formname:
        frm = eval(formname)
    else:
        frm = modelform_factory(eval(modelname), exclude=('active',))
    form = frm(instance=obj)
    if request.method == 'POST':
        form = frm(request.POST, request.FILES, instance=obj)
        if model_has_field(eval(modelname), 'slug'):
            check = eval(modelname).objects.filter(slug=slugify(request.POST.get('name'))).exclude(id=obj.id)
        elif model_has_field(eval(modelname), 'name'):
            check = eval(modelname).objects.filter(name=request.POST.get('name')).exclude(id=obj.id)
        if form.is_valid():
            if not check:
                f = form.save(commit=False)
                f.save()
                edit_done = True
                return HttpResponseRedirect('/manage/?key='+key)
            else:
                error = "Name Already exists"
        else:
            error = "Invalid Form"
    return render_to_response('manage/add-form.html', locals(), context_instance=RequestContext(request))




def adminlogin(request, next=''):
    # admin login function,
    # if next is there it will redirect to next url
    # if not it will load dashboard
    user = request.user
    next = request.GET.get('next')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        next = request.POST.get('next')
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            if next:
                return HttpResponseRedirect(next) 
            else:
                return HttpResponseRedirect('/manage-home/')
        else:
            # invalid login
            form = LoginForm()
            message = 'Please enter a correct username and password'
            return render_to_response('manage/login.html', locals(), context_instance=RequestContext(request))
    else:
        form = LoginForm()
        return render_to_response('manage/login.html',locals(),context_instance=RequestContext(request))   
    return render_to_response('manage/login.html', locals(), context_instance=RequestContext(request))


def adminlogout (request):
    # admin logout function
    logout(request)
    return HttpResponseRedirect('/manage/admin/')

def home(request):
    # dashboard
    user = request.user
    today = date.today()
    if user.id is not None:
        p=date.today()+timedelta(-1)
        return render_to_response('manage/base.html',locals(), context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/manage/admin/')


def manage(request):
    # common function to list all items based in key
    # item_list : objects list of final result
    # key : is the model name we are sending, so that based on key, very easy to query
    key = request.GET.get('key', '')
    home = request.GET.get('home', '')
    user = request.user
    objects_list = ''
    item_list = ''

    if key == 'article':
        # all article list
        article_list = Article.objects.all()
        item_list = article_list
        title = "Article"
    elif key == 'user':
        # all user list
        user_list = User.objects.all()
        item_list = user_list
        title = 'User'
    elif key == 'frontmenu':
        # all menus list
        item_list = FrontMenu.objects.all()
    elif key == 'our_banners':
        # all banners list
        item_list = HomeBanners.objects.all()
    elif key == 'our_team':
        # all team list
        item_list = Team.objects.all().order_by('-listingOrder')
    elif key == 'comments':
        # all comments list
        model = 'Comments'
        formname = 'CommentForm'
        pub = request.GET.get('pub', '')
        if pub == 'True':
            item_list = Comments.objects.filter(publish=True).order_by('-modified_on')[:5000]
        else:
            item_list = Comments.objects.filter(publish=False).order_by('-modified_on')[:5000]
        ct_object = {obj.id: str(obj.relatedTo) if obj.relatedTo else None for obj in item_list}
    elif key == 'archive':
        # all archive list
        item_list = Archive.objects.all()
        model = 'Archive'
        formname = 'ArchiveForm'
    elif key == 'photofeature':
        # all PhotoFeature list
        item_list = PhotoFeature.objects.all()
        model = 'PhotoFeature'
        formname = 'PhotoFeatureForm'
    elif key == 'job':
        # all job list
        item_list = Job.objects.all()
        if lang:
            item_list = item_list.filter(language=language)
    elif key == 'gallery':
        # all gellary list
        model = 'Gallery'
        item_list = Gallery.objects.all()
    elif key == 'ads':
        # all Ads list
        model = 'Ads'
        item_list = Ads.objects.all()
    elif key == 'manage-gallery':
        # all image list of particular gallery(objid)
        objid = request.GET.get('objid')
        obj = Gallery.objects.get(id=objid)
    elif key == 'columnists':
        # all Columnists list
        item_list = Columnists.objects.all()
        model = 'Columnists'
        formname = 'ColumnistsForm'
    elif key == 'columns':
        # all Columnists list
        item_list = Columns.objects.all()
        model = 'Columns'
        formname = 'ColumnsForm'
    elif key == 'columncategory':
        # all Columnists list
        item_list = ColumnCategory.objects.all()
        model = 'ColumnCategory'
        formname = 'ColumnCategoryForm'
    elif key == 'currentissue':
        # all currentissue list
        item_list = Currentissue.objects.all()
        model = 'Currentissue'
        formname = 'CurrentissueForm'
    elif key == 'photofeatureimage':
        # all PhotoFeature Images list
        item_list = PhotoFeatureImages.objects.all()
        model = 'PhotoFeatureImages'
        formname = 'PhotoFeatureImageForm'
    elif key == 'subscription':
        # all PhotoFeature Images list
        item_list = Subscription.objects.filter(status="Success")
        model = 'Subscription'
        formname = 'SubscriptionForm'
    elif key == 'writetous':
        # all PhotoFeature Images list
        item_list = WriteToUs.objects.all()
        model = 'WriteToUs'
        formname = 'WriteToUsForm'
    elif key == "aboutus":
        # all About Us Content
        item_list = AboutUs.objects.all()
        model = 'AboutUs'
        formname = 'AboutUsForm'
    elif key == "editor":
        # all About Us Content
        item_list = Editor.objects.all()
        model = 'Editor'
        formname = 'EditorForm'
    elif key == "newsletter":
        # all About Us Content
        item_list = Subscribe.objects.all()
        model = 'NewsLetter'
    elif key == "manage-aboutus":
        objid = request.GET.get('objid')
        item_list = Image.objects.filter(content_type=ContentType.objects.get(name__iexact = 'about us'), object_id=objid)
        obj = AboutUs.objects.get(id=objid)
        model = 'Image'
        formname = 'ImageForm'
    return render_to_response('manage/manage.html', locals(), context_instance=RequestContext(request))


# ----------------------------------ACTIVATE AND DEACTIVATE ----------------------------------------------#


def activate(request):
    # common activate function
    # next : redirect url after activation
    # model_name : object model name
    # pk : id the object to activate
    next = request.GET.get('next')
    model_name = request.GET.get('key')
    pk = request.GET.get('pk')
    obj = eval(model_name).objects.get(pk=pk)
    if hasattr(obj, 'active'):
        obj.active = True
    if hasattr(obj, 'is_active'):
        obj.is_active = True
    obj.save()
    return HttpResponseRedirect(next)


def deactivate(request):
    # common deactivate function
    # next : redirect url after deactivate
    # model_name : object model name
    # pk : id the object to deactivate
    next = request.GET.get('next')
    model_name = request.GET.get('key')
    pk = request.GET.get('pk')
    obj = eval(model_name).objects.get(pk=pk)
    if hasattr(obj, 'active'):
        obj.active = False
    if hasattr(obj, 'is_active'):
        obj.is_active = False
    obj.save()
    return HttpResponseRedirect(next)

def delete_func(request):
    # common delete function
    # next : redirect url after deactivate
    # model_name : object model name
    # pk : id the object to delete
    next = request.GET.get('next')
    model_name = request.GET.get('key')
    pk = request.GET.get('pk')
    obj = eval(model_name).objects.get(pk=pk).delete()
    return HttpResponseRedirect(next)

# ---------------------------------Change User Password ---------------------------------#


def change_password(request):
    # change password function of users
    pk = request.GET.get('pk')
    user_obj = User.objects.get(pk=pk)
    new_pwd = request.POST.get('new_pwd')
    chg_pwd = request.POST.get('chg_pwd')
    if new_pwd and chg_pwd and request.method == 'POST':
        user_obj.set_password(chg_pwd)
        user_obj.save()
        return HttpResponseRedirect('/manage/?key=user')
    return render_to_response('manage/change-password.html', locals(), context_instance=RequestContext(request))


#----------------------------------Article ----------------------------------------------#

def add_article(request):
    # add form of article
    # checking headline as unique
    form = ArticleForm()
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            check=Article.objects.filter(slug__iexact=slugify(request.POST.get('headline')))
            if not check:
                obj=form.save(commit=False)
                obj.slug=slugify(request.POST.get('headline'))
                obj.save()
                form.save_m2m()
                return HttpResponseRedirect('/manage/?key=article')
            else:
                error= "Article headline already exist"
                return render_to_response('manage/add_article.html', locals(), context_instance=RequestContext(request))
        else:
            form = ArticleForm(request.POST, request.FILES)
        return render_to_response('manage/add_article.html', locals(), context_instance=RequestContext(request))
    else:
        form = ArticleForm()
    return render_to_response('manage/add_article.html', locals(), context_instance=RequestContext(request))

def edit_article(request, art_id=''):
    # edit form of article
    edit = True
    if art_id == '':
        art_id = request.GET.get('art_id', '')
    article = Article.objects.get(id=art_id)
    tags_list = [i.name for i in article.keywords.all()]
    tags = ', '.join(tags_list)
    form = ArticleForm(instance=article)
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            f = form.save(commit=False)
            f.save()
            form.save_m2m()
            edit_done=True
            return render_to_response('manage/add_article.html', locals(), context_instance=RequestContext(request))
        else:
            form = ArticleForm(request.POST, request.FILES, instance=article )
    return render_to_response('manage/add_article.html', locals(), context_instance=RequestContext(request))



def delete_article(request, id='',next=''):
    # deactivate function for article
    if id == '':
        id = request.GET.get('id')
    if next == "":
        next = request.GET.get('next')
    obj = Article.objects.get(id=id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect(next)

def activate_article(request, id='',next=''):
    # activate function for article
    if id == '':
        id = request.GET.get('id')
    if next == "":
        next = request.GET.get('next')
    obj = Article.objects.get(id=id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect(next)


#----------------------------------Image ----------------------------------------------#

def add_image(request):
    # add function of image module, in which image module is a generic foriegn key
    next = request.GET.get('next')
    key = request.GET.get('key')
    gal_id = request.GET.get('ct_id')
    if request.method== "POST":
        form=ImageForm(request.POST,request.FILES)
        if form.is_valid():
            obj= form.save(commit=False)
            obj.content_type = ContentType.objects.get(name__iexact = key)
            obj.object_id = gal_id
            obj.listingOrder = 0
            obj.status = 'PU'
            obj.save()
            if key == 'article':
                return HttpResponseRedirect('/manage/?key=manage-sections&art_id='+gal_id)
            if key == 'about us':
                return HttpResponseRedirect('/manage/?key=aboutus')
            else:
                return HttpResponseRedirect(next+'&art_id='+gal_id+'&event_id='+gal_id+'&objid='+gal_id)
        else:
            form=ImageForm(request.POST,request.FILES)
        return render_to_response('manage/add_image.html', locals(), context_instance=RequestContext(request))
    else:
        form=ImageForm()
    return render_to_response('manage/add_image.html', locals(), context_instance=RequestContext(request))


def edit_image(request, img_id=''):
    # edit function of image module
    next = request.GET.get('next')
    if img_id == '':
        img_id=request.GET.get('img_id')
    from mcms.models import Image
    image=Image.objects.get(id=img_id)
    art_id=request.GET.get('art_id')
    key = request.GET.get('key')
    edit = True
    if request.method== "POST":
        form=ImageForm(request.POST,request.FILES,instance=image)
        if form.is_valid():
            form.save()
            if key == 'article':
                return HttpResponseRedirect('/manage/?key=manage-sections&art_id='+art_id)
            elif key == "about us":
                return HttpResponseRedirect('/manage/?key=aboutus')
            else:
                return HttpResponseRedirect(next+'&art_id='+art_id+'&event_id='+art_id)
        else:
            form=ImageForm(request.POST,request.FILES)
        return render_to_response('manage/add_image.html', locals(), context_instance=RequestContext(request))
    else:
        form=ImageForm(instance=image)
    return render_to_response('manage/add_image.html', locals(), context_instance=RequestContext(request))

def delete_image(request, img_id='',key=''):
    # deactivate function of image module
    if key == '':
        key = request.GET.get('key')
    next = request.GET.get('next')
    art_id = request.GET.get('art_id','')
    event_id = request.GET.get('event_id','')
    if img_id == '':
        img_id = request.GET.get('img_id')
    obj = Image.objects.get(id=img_id)
    obj.active = False
    obj.save()
    if key =='manage-articles':
        return HttpResponseRedirect('/manage/?key=manage-articles&art_id='+art_id)
    elif key == 'manage-event':
        return HttpResponseRedirect('/manage/?key=manage-event&event_id='+event_id)
    elif key == 'manage-sections':
		return HttpResponseRedirect('/manage/?key=manage-sections&art_id='+art_id)
    elif key == "about us":
        return HttpResponseRedirect('/manage/?key=aboutus')
    else:
        return HttpResponseRedirect('/manage-home/')



def activate_image(request, img_id='',key=''):
    # activate function of image module
    if key == '':
        key = request.GET.get('key')
    next = request.GET.get('next')
    art_id = request.GET.get('art_id','')
    event_id = request.GET.get('event_id','')
    if img_id == '':
        img_id = request.GET.get('img_id')
    obj = Image.objects.get(id=img_id)
    obj.active = True
    obj.save()
    if key =='manage-articles':
        return HttpResponseRedirect('/manage/?key=manage-articles&art_id='+art_id)
    elif key == 'manage-sections':
        return HttpResponseRedirect('/manage/?key=manage-sections&art_id='+art_id)
    elif key == 'manage-event':
        return HttpResponseRedirect('/manage/?key=manage-event&event_id='+event_id)
    elif key == "about us":
        return HttpResponseRedirect('/manage/?key=aboutus')
    else:
        return HttpResponseRedirect('/manage-home/')

#--------------------------------Media Videos---------------------------#

def add_videos(request):
    lang = request.session.get('lang')
    if lang:
        language = Language.objects.get(slug='english')
    # add form of videos
    form = VideosForm()
    home = request.GET.get('home')
    if request.method == 'POST':
        form = VideosForm(request.POST,request.FILES)
        category = Category.objects.get(name='Home-Page')
        if form.is_valid():
            f = form.save()
            if lang:
                f.language = language
            if home == 'true':
                f.display_in_home = True
                f.category = category
            f.save()
            if home == 'true':
                return HttpResponseRedirect('/manage/?key=videos&home=true')
            else:
                return HttpResponseRedirect('/manage/?key=videos')
        else:
            form = VideosForm(request.POST)
    return render_to_response('manage/add_videos.html', locals(), context_instance=RequestContext(request))

def edit_videos(request):
    # edit form of videos
    edit = True
    home = request.GET.get('home')
    id_edit = request.GET.get('videos-videos_id')
    videos = Videos.objects.get(id=id_edit)
    form = VideosForm(instance = videos)
    if request.POST:
        form = VideosForm(request.POST,request.FILES, instance = videos)
        if form.is_valid():
            form.save()
            edit_done = True
            msg = "edited successfully"
            success = True
            if home == 'true':
                return HttpResponseRedirect('/manage/?key=videos&home=true')
            else:
                return HttpResponseRedirect('/manage/?key=videos')
        else:
                 msg='Invalid form'
    return render_to_response('manage/add_videos.html', locals(), context_instance=RequestContext(request))


def delete_videos(request):
    # deactivate form of videos
    videos_id = request.GET.get('videos-videos_id')
    home = request.GET.get('home')
    obj = Videos.objects.get(id=videos_id)
    obj.active = False
    obj.save()
    if home == 'true':
        return HttpResponseRedirect('/manage/?key=videos&home=true')
    else:
        return HttpResponseRedirect('/manage/?key=videos')

def activate_videos(request):
    # activate form of videos
    videos_id = request.GET.get('videos-videos_id')
    home = request.GET.get('home')
    obj = Videos.objects.get(id=videos_id)
    obj.active = True
    obj.save()
    if home == 'true':
        return HttpResponseRedirect('/manage/?key=videos&home=true')
    else:
        return HttpResponseRedirect('/manage/?key=videos')

def publish(request, pk='',next=''):
    # deactivate function for artile
    if pk == '':
        id = request.GET.get('pk')
    if next == "":
        next = request.GET.get('next')
    obj = Comments.objects.get(id=id)
    obj.publish = True
    obj.save()
    return HttpResponseRedirect(next)

def unpublish(request, pk='',next=''):
    # activate function for article
    if pk == '':
        id = request.GET.get('pk')
    if next == "":
        next = request.GET.get('next')
    obj = Comments.objects.get(id=id)
    obj.publish = False
    obj.save()
    return HttpResponseRedirect(next)

from django.http import JsonResponse
def publishcomment(request,publish):
    # Your usual logic
    try:
        pk = request.POST.get('pk')
        key = request.POST.get('key')
        obj = Comments.objects.get(id=pk)
        if publish == 'publish':
            obj.publish = True
        else:
            obj.publish = False
        obj.save()
        return JsonResponse({'status': 'success'})
    except:
        return JsonResponse({'status': 'failed'})


#--------------------------------Front Menu----------------------------------------#
def add_frontmenu(request):
    # add form of front menu
    lang = request.session.get('lang')
    language = Language.objects.get(slug='english')
    f = get_frontmenuform(language)
    form = f()
    if request.method == "POST":
        form = f(request.POST,request.FILES)
        if form.is_valid():
            check = FrontMenu.objects.filter(slug=request.POST.get('slug'),parent=None, active=True,language=language)
            pt = request.POST.get('parent')
            check1 = ''
            if not check:
                faqs = []
                art = []
                expts = []
                name = request.POST.get('name')
                fq = request.POST.getlist('faq_category')
                faqs = [FAQ_Category.objects.get(id=int(i)) for i in fq]
                arts = request.POST.getlist('article')
                art = [Article.objects.get(id=int(i)) for i in arts]
                rel_video = request.POST.getlist('related_videos')
                rel_video_list = [Videos.objects.get(id=int(i)) for i in rel_video]
                keywords = request.POST.get('keywords')
                tags = keywords.split(',')
                tag_list = [KeyWord.objects.get_or_create(name=i)[0] for i in tags]
                f = form.save(commit=False)
                f.language = language
                f.slug = slugify(name)
                f.one_page = True
                f.save()
                f.faq_category.add(*faqs)
                f.article.add(*art)
                f.keywords.add(*tag_list)
                f.related_videos.add(*rel_video_list)
                added = True
                return HttpResponseRedirect('/manage/?key=frontmenu')
            else:
                msg = "name already exist or listing order already exist"
                form = f(request.POST, request.FILES)
                return render_to_response('manage/add_frontmenu.html', locals(), context_instance=RequestContext(request))
        else:
            form = f(request.POST, request.FILES)
        return render_to_response('manage/add_frontmenu.html', locals(), context_instance=RequestContext(request))
    else:
        form = f()
    return render_to_response('manage/add_frontmenu.html', locals(), context_instance=RequestContext(request))
    
def edit_frontmenu(request):
    # edit form of front menu
    edit = True
    id_edit = request.GET.get('frontmenu-frontmenu_id')
    frontmenu = FrontMenu.objects.get(id=id_edit)
    language = Language.objects.get(slug='english')
    tags_list = [i.name for i in frontmenu.keywords.all()]
    tags = ', '.join(tags_list)
    f = get_frontmenuform(language)
    form = f(instance = frontmenu)
    check,check1 = '',''
    if request.POST:
        form = f(request.POST,request.FILES, instance = frontmenu)
        if form.is_valid():
            form.save(commit=False)
            check = FrontMenu.objects.filter(name = request.POST.get('name'),parent = None, active=True,language=None).exclude(id=frontmenu.id).exists()
            check1 = ''
            if not check :
                keywors = request.POST.get('keywords')
                fq = request.POST.getlist('faq_category')
                arts = request.POST.getlist('article')
                rel_video = request.POST.getlist('related_videos')
                f = form.save(commit=False)
                f.keywords.clear()
                f.faq_category.clear()
                f.article.clear()
                f.related_videos.clear()
                tags1 = keywors.split(',')
                faqs = [FAQ_Category.objects.get(id=int(i)) for i in fq]
                art = [Article.objects.get(id=int(i)) for i in arts]
                rel_video_list = [Videos.objects.get(id=int(i)) for i in rel_video]
                tag_list1 = [KeyWord.objects.get_or_create(name=i)[0] for i in tags1]
                f.save()
                f.faq_category.add(*faqs)
                f.article.add(*art)
                f.keywords.add(*tag_list1)
                f.related_videos.add(*rel_video_list)
                edit_done = True
                msg = "edited successfully"
                success = True
            else:
                msg = "name already exist or listing order already exist"
    return render_to_response('manage/add_frontmenu.html', locals(), context_instance=RequestContext(request))

def delete_frontmenu(request):
    # deactivate form of front menu
    frontmenu_id = request.GET.get('frontmenu-frontmenu_id')
    obj = FrontMenu.objects.get(id=frontmenu_id)
    obj.active = False
    obj.save()
    return HttpResponseRedirect('/manage/?key=frontmenu')

def activate_frontmenu(request):
    # activate form of front menu
    frontmenu_id = request.GET.get('frontmenu-frontmenu_id')
    obj = FrontMenu.objects.get(id=frontmenu_id)
    obj.active = True
    obj.save()
    return HttpResponseRedirect('/manage/?key=frontmenu')


def add_editor(request):
    # add form of videos
    form = EditorForm()
    if request.method == 'POST':
        form = EditorForm(request.POST)
        if form.is_valid():
            uname = request.POST.get('username')
            pwd = request.POST.get('password')
            fname = request.POST.get('first_name')
            lname = request.POST.get('last_name')
            if User.objects.filter(username=uname):
                error = "User already registered / or subscribed"
                return render_to_response('manage/add_editor.html', locals(), context_instance=RequestContext(request))
            else:
                u = User.objects.create_user(username=uname, password=pwd,first_name=fname,last_name=lname,email=uname)
                Editor.objects.create(user=u, editor_type = "Subscriber")
            return HttpResponseRedirect('/manage/?key=editor')
        else:
            form = EditorForm(request.POST)
    return render_to_response('manage/add_editor.html', locals(), context_instance=RequestContext(request))

#--------------------------------Our Banners---------------------------#

def add_our_banners(request):
    # add form of home banners
    lang = request.session.get('lang')
    if lang:
        language = Language.objects.get(slug='english')
    home = request.GET.get('home')
    form = OurBannersForm()
    if request.method == "POST":
        form = OurBannersForm(request.POST,request.FILES)
        if form.is_valid():
            check = HomeBanners.objects.filter(listing_order__iexact=request.POST.get('listing_order'))
            if not check :
                f = form.save(commit=False)
                f.save()
                added = True
                return HttpResponseRedirect('/manage/?key=our_banners')
            else:
                error = "listing order already exist"
                form = OurBannersForm(request.POST)
                return render_to_response('manage/add_our_banners.html', locals(), context_instance=RequestContext(request))
    return render_to_response('manage/add_our_banners.html', locals(), context_instance=RequestContext(request))

def edit_our_banners(request):
    # edit form of home banners
    edit = True
    home = request.GET.get('home')
    id_edit = request.GET.get('our_banners-our_banners_id')
    our_banners = HomeBanners.objects.get(id=id_edit)
    form = OurBannersForm(instance = our_banners)
    if request.POST:
        form = OurBannersForm(request.POST,request.FILES, instance = our_banners)
        if form.is_valid():
            form.save(commit=False)
            check = HomeBanners.objects.filter(listing_order__iexact=request.POST.get('listing_order')).exclude(id=our_banners.id).exists()
            if not check :
                f = form.save(commit=False)
                f.save()
                edit_done = True
                msg = "edited successfully"
                success = True
                return HttpResponseRedirect('/manage/?key=our_banners')
            else:
                error = "listing order already exist"
    return render_to_response('manage/add_our_banners.html', locals(), context_instance=RequestContext(request))

def delete_our_banners(request):
    # deactivate form of home banners
    our_banners_id = request.GET.get('our_banners-our_banners_id')
    home = request.GET.get('home')
    obj = HomeBanners.objects.get(id=our_banners_id)
    obj.active = False
    obj.save()
    if home == 'true':
        return HttpResponseRedirect('/manage/?key=our_banners&home=true')
    else:
        return HttpResponseRedirect('/manage/?key=our_banners')

def activate_our_banners(request):
    # activate form of home banners
    our_banners_id = request.GET.get('our_banners-our_banners_id')
    home = request.GET.get('home')
    obj = HomeBanners.objects.get(id=our_banners_id)
    obj.active = True
    obj.save()
    if home == 'true':
        return HttpResponseRedirect('/manage/?key=our_banners&home=true')
    else:
        return HttpResponseRedirect('/manage/?key=our_banners')
