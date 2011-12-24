# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

def home(request):
    return render_to_response('frontend/home.html',
	        context_instance=RequestContext(request))

def message(request):
	return render_to_response('frontend/message.html',
			context_instance=RequestContext(request))

def admin_message(request):
	return render_to_response('frontend/admin_message.html',
			context_instance=RequestContext(request))
