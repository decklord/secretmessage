# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,get_object_or_404
from django.template import RequestContext
from api.models import Message

def home(request):
    return render_to_response('frontend/home.html',
	        context_instance=RequestContext(request))

def message(request,code):

	message = Message.objects.get(code=code)

	return render_to_response('frontend/message.html',{'message':message},context_instance=RequestContext(request))

def admin_message(request):
	return render_to_response('frontend/admin_message.html',
			context_instance=RequestContext(request))
