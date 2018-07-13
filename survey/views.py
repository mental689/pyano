from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
import glog as log
import datetime, time

# Create your views here.

def index(request):
    template = loader.get_template('survey/index.html')
    context = {"message": "Welcome to PsYchological ANnOtation page."}
    return HttpResponse(template.render(context, request))

@require_GET
def job(request):
    if not request.user.is_authenticated:
        return redirect(to="{}?next=/job/".format(settings.LOGIN_URL))
    # get current timestamp to measure the performance latter
    start = time.time()
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

@csrf_protect
@require_POST
def submission(request):
    if not request.user.is_authenticated:
        return redirect(to="{}?next=/".format(settings.LOGIN_URL))
    log.info(request.POST.get("annotations"))
    return redirect(to="complete")


def complete(request):
    return HttpResponse("Thank you, your submission is received! Please wait while we are reviewing your submission!")


# Views need authentication

@require_GET
def review_video(request):
    if not request.user.is_authenticated:
        return redirect(to="{}?next=/review_video/".format(settings.LOGIN_URL))
    else:
        return HttpResponse("Welcome to PYANO reviewer page")


def register(request):
    if request.user.is_authenticated:
        return redirect('')
    if request.method == "GET":
        form = UserCreationForm()
    else:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('')
    return render(request, "registration/register.html", {"form": form})


def profile(request):
    if not request.user.is_authenticated:
        return redirect(to="{}?next=/profile".format(settings.LOGIN_URL))
    return HttpResponse("Welcome to PYANO! {}".format(request.user))