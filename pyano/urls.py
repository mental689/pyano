"""pyano URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import include
from django.contrib.auth import views as auth_views
from pyano2.class_views.user import RegisterView, ProfileView
from examples.shoplift.shoplift import ShopliftSummaryView, QBESearchView

from django.conf import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/', auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    url(r'^accounts/logout/', auth_views.LogoutView.as_view(), name="logout"),
    url(r'^accounts/profile/', ProfileView.as_view(), name="profile"),
    url(r'^register/', RegisterView.as_view(), name="register"),
    url(r'^oauth/', include('social_django.urls', namespace='social')),  # <--
    url(r'^examples/shoplift/', ShopliftSummaryView.as_view(), name='shoplift_example'),
    url(r'^examples/qbe/', QBESearchView.as_view(), name='qbe_example'),
    url(r'^', include('pyano2.urls')),
]

if 'survey' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^survey/', include('survey.urls'))
    ]

if 'newsletter' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^newsletter/', include('newsletter.urls'))
    ]

if 'tinymce' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^tinymce/', include('tinymce.urls'))
    ]
