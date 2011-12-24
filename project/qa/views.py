# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

def qunit(request):
    return render_to_response('qa/qunit.html',
            context_instance=RequestContext(request))

@csrf_exempt
def echo(request):
    return HttpResponse(request.raw_post_data)
