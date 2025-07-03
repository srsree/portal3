from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import *
from django.contrib.auth import authenticate, login, logout
from django.template import Context, loader,RequestContext
from django.http import HttpResponseRedirect,HttpResponse,Http404
from faq.models import *

def faq(request):
    faq_cat = FAQ_Category.objects.filter(is_active=True)
    ans = Question.objects.filter(is_active=True)
    return render_to_response('faq.html',locals(),context_instance=RequestContext(request))
