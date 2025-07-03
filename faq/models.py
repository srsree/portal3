from django.db import models
from django.contrib import admin
from django.forms import ModelForm
from ckeditor.fields import RichTextField
from django import forms
from django.contrib.contenttypes.models import ContentType
from mcms.models import KeyWord

class FAQ_Category(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    slug = models.SlugField(max_length = 600, blank=True, null=True)
    language = models.ForeignKey('mcms.Language', blank=True, null=True)
    is_active = models.BooleanField(default = True)
    added_on = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', blank=True, null=True)
    frontmenu = models.ForeignKey('mcms.FrontMenu', blank=True, null=True, related_name="Related FrontMenu for faq")
    keywords = models.ManyToManyField(KeyWord, blank=True, null=True, related_name="Related Keywords for faq")
    display_in_frontend = models.BooleanField(default=False)

    def get_childs(self):
        return FAQ_Category.objects.filter(parent = self, is_active=True)

    def get_questions(self):
        return Question.objects.filter(category__id=self.id)


class Question(models.Model):
    category = models.ForeignKey(FAQ_Category, on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    added_on = models.DateTimeField(auto_now_add=True)


    def get_answer(self):
        return Answer.objects.filter(question__id=self.id)

    def __unicode__(self):
        return "%s"%(self.question)
        
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = RichTextField()
    is_active = models.BooleanField(default=True)
    added_on = models.DateTimeField(auto_now_add=True)  

    def __unicode__(self):
        return "%s"%(self.answer)
        
### ****************Model Forms****************
def get_faq_lang_form(obj):
    lang = obj.language
    class FAQ_CategoryForm(ModelForm):
        from mcms.models import FrontMenu
        parent = forms.ModelChoiceField(queryset=FAQ_Category.objects.filter(language__slug="english", is_active=True), required=False)
        frontmenu = forms.ModelChoiceField(queryset=FrontMenu.objects.filter(language=lang, active=True), required=True)
        class Meta:
            model = FAQ_Category
            exclude = ('is_active', 'language', 'display_in_frontend', 'slug', 'keywords', 'doc_type')
    return FAQ_CategoryForm

class FaqQuestionForm(ModelForm):
    question = forms.CharField(label=('Question'),max_length=500,widget=forms.Textarea(attrs={'cols': 50, 'rows': 4}),required=True)
    class Meta:
        model = Question
        exclude = ('category', 'is_active')

class FaqAnswerForm(ModelForm):
    class Meta:
        model = Answer
        exclude = ('question', 'is_active')
