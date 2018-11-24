from django.urls import path
from . import views
from pyano2.class_views.keyword_search import KeywordSearchView
from pyano2.class_views.index import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('keyword_search/', KeywordSearchView.as_view(), name="keyword_search")
]