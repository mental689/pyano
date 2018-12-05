from django.urls import path
from . import views
from pyano2.class_views.keyword_search import KeywordSearchView
from pyano2.class_views.index import IndexView
# from pyano2.class_views.about import Aboutview
from pyano2.class_views.invitation import InvitationView

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    # path('about/', Aboutview.as_view(), name='about'),
    path('keyword_search/', KeywordSearchView.as_view(), name="keyword_search"),
    path('invite/', InvitationView.as_view(), name="invitation")
]