from django.conf import settings
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View

from pyano2.forms import SignUpForm


class RegisterView(View):
    template_name = 'registration/register.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('')
        form = SignUpForm()
        return render(request, template_name=self.template_name, context={"form": form})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('')
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
        return render(request, template_name=self.template_name, context={"form": form})


class ProfileView(View):
    template_name = 'registration/profile.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/profile".format(settings.LOGIN_URL))
        return render(request, template_name=self.template_name, context={})

