from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.

def index(request):
    template = loader.get_template('survey/index.html')
    context = {"message": "Welcome to PsYchological ANnOtation page."}
    return HttpResponse(template.render(context, request))

def job(request):
    yid = request.GET.get("yid")
    if yid is not None:
        type = "youtube"
        source = ""
    else:
        type = "pyano"
        vid = request.GET.get("vid")
    template = loader.get_template('survey/job_page.html')
    context = {"yid": yid, "type": type}
    return HttpResponse(template.render(context, request))