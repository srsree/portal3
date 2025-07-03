# -*- encoding: utf-8 -*-
# all mcms forms
from django import forms
from django.forms import widgets
from django.forms.extras.widgets import SelectDateWidget
from datetime import *
from django.db.models import Q
import re
from django.forms import ModelForm
from django.template.defaultfilters import slugify
from mcms.models import *
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.conf import settings 
from faq.models import *
from ccavenue.models import *

Size_CHOICES = ((u'S', 'Small'),(u'M', 'Medium'),(u'L', 'Large'),)
title_CHOICES = (('u''Mister', 'Mr.'),('u''Miss', 'Ms.'))
TITLE_CHOICES = (('u''Mr.', 'Mr.'),('u''M.s', 'Ms.'),('u''Miss.', 'Miss.'),('u''Mrs.', 'Mrs.'),('u''Dr.', 'Dr.'),('u''Colonel.', 'Colonel.'))
NEWS_CHOICES = (('', '---------'),('General news', 'General news'),('BC News','BC News'))

class LoginForm(forms.Form):
    # login form to access the site from backend and frontend
    # default login form
    username = forms.CharField(label=u'Email Address:* ', required=True)
    password = forms.CharField(label=u'Password:* ', widget=forms.PasswordInput(), required=True)


from django.core.files.images import get_image_dimensions
class ImageForm(ModelForm):
    # image form
   class Meta:
       model=Image
       exclude=('content_type', 'object_id', 'title', 'listingOrder', 'status','URL', 'active')
       def clean_picture(self):
           picture = self.cleaned_data.get("image")
           if not picture:
               raise forms.ValidationError("No image!")
           else:
               w, h = get_image_dimensions(picture)
               if w != 930:
                   raise forms.ValidationError("The image is %i pixel wide. It's supposed to be 930px" % w)
               if h != 300:
                   raise forms.ValidationError("The image is %i pixel high. It's supposed to be 300px" % h)
           return picture


class ArticleForm(forms.ModelForm):
    # ArticleForm
    # for all stories this is the form
    class Meta:
        model = Article
        exclude = ('slug', 'active', 'created_by', 'text', 'extract', 'tags', 'keywords', 'language', 'article_type', 'display_in_frontend', 'doc_type')

class ArchiveForm(ModelForm):
    # ArchiveForm
    class Meta:
        model = Archive
        exclude = ('active',)

class PhotoFeatureForm(ModelForm):
    # PhotoFeatureForm
    class Meta:
        model = PhotoFeature
        exclude = ('active',)


class PhotoFeatureImageForm(ModelForm):
    # PhotoFeatureImageForm
    class Meta:
        model = PhotoFeatureImages
        exclude = ('active','URL')

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['photo_feature', 'name', 'image', 'description']

class NewsForm(forms.ModelForm):
    # NewsForm
    class Meta:
        model = News
        exclude = ('active','created_on', 'language', 'tags')


class GlossaryForm(forms.ModelForm):
    # GlossaryForm
    class Meta:
        model = Glossary
        exclude = ('active','created_on')

class WriteToUsForm(forms.ModelForm):
    # WriteToUsForm
    class Meta:
        model = WriteToUs
        exclude = ('active','created_on')


class AboutUsForm(forms.ModelForm):
    # AboutUsForm
    class Meta:
        model = AboutUs
        exclude = ('active','created_on')


class AttachmentForm(forms.ModelForm):
    # AttachmentForm
    class Meta:
        model = Attachment
        exclude = ('active','created_on','content_type', 'object_id')

class LinkForm(forms.ModelForm):
    # LinkForm
    class Meta:
        model = Link
        exclude = ('active','created_on','content_type', 'object_id')



class VideosForm(forms.ModelForm):
    # VideosForm
    class Meta:
        model = Videos
        exclude = ('active','featured', 'summary', 'language', 'category')



def get_frontmenuform(language):
    # Forntmenu form in which all menus comes under this form
    class FrontMenuForm(forms.ModelForm):
        parent = forms.ModelChoiceField(queryset=FrontMenu.objects.filter(parent=None, language=language), required=False)
        article = forms.ModelMultipleChoiceField(queryset=Article.objects.filter(language=language, active=True, display_in_frontend=True), required=False)
        related_videos = forms.ModelMultipleChoiceField(queryset=Videos.objects.filter(language=language, active=True), required=False)
        faq_category = forms.ModelMultipleChoiceField(queryset=FAQ_Category.objects.filter(language=language, is_active=True, display_in_frontend=True), required=False)
        class Meta:
            model = FrontMenu
            exclude = ('active','created_on','one_page', 'url', 'keywords','language','slug')
    return FrontMenuForm

class CategoryForm(forms.ModelForm):
    # CategoryForm
    class Meta:
        model = Category
        exclude = ('active','created_on')

class OurBannersForm(forms.ModelForm):
    # Our_BannersForm
    class Meta:
        model = HomeBanners
        exclude = ('active', 'created_on', 'language')


class CommentForm(forms.ModelForm):
    # Comments Form
    class Meta:
        model = Comments
        exclude = ('active', 'created_on', 'modified_on','publish','content_type','object_id','relatedTo')

class ColumnistsForm(forms.ModelForm):
    # ColumnistsForm
    class Meta:
        model = Columnists
        exclude = ('active', 'created_on', 'modified_on','slug','link')


class ColumnCategoryForm(forms.ModelForm):
    # ColumnistsForm
    class Meta:
        model = ColumnCategory
        exclude = ('active', 'created_on', 'modified_on','slug','language')

class ColumnsForm(forms.ModelForm):
    # ColumnistsForm
    class Meta:
        model = Columns
        exclude = ('active', 'created_on', 'modified_on','slug','language')

class EditorForm(forms.Form):
    Editor_Choices = (('Subscriber','Subscriber'),('Editor','Editor'))
    username = forms.CharField(label=u'Email Address:* ', required=True)
    password = forms.CharField(label=u'Password:* ', widget=forms.PasswordInput(), required=True)
    first_name = forms.CharField(label=u'First Name: ', required=False)
    last_name = forms.CharField(label=u'Last Name ', required=False)
    editor_type = forms.ChoiceField(choices=Editor_Choices)

class CurrentissueForm(forms.ModelForm):
    # CurrentissueForm
    class Meta:
        model = Currentissue
        exclude = ('active', 'created_on', 'modified_on','slug')

class SubscriptionForm(forms.ModelForm):
    # LinkForm
    class Meta:
        model = Subscription
        exclude = ('active','created_on')
