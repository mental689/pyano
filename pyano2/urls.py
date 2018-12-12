from django.urls import path
from . import views
from pyano2.class_views.keyword_search import KeywordSearchView
from pyano2.class_views.index import IndexView
# from pyano2.class_views.about import Aboutview
from pyano2.class_views.invitation import InvitationView, AcceptInvitationView, DeclineInvitationView, AlternativeRecommendationView
from pyano2.class_views.vatic import VATICIndexView, VATICJobView, VATICBoxesForJobView, VATICValidateJobView, VATICSaveJobView, VATICListView

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    # path('about/', Aboutview.as_view(), name='about'),
    path('keyword_search/', KeywordSearchView.as_view(), name="keyword_search"),
    path('invite/', InvitationView.as_view(), name="invitation"),
    path('accept/', AcceptInvitationView.as_view(), name="accept_invitation"),
    path('decline/', DeclineInvitationView.as_view(), name='decline_invitation'),
    path('recommend_after_decline/', AlternativeRecommendationView.as_view(), name='recommend_alternatives'),
    path('vatic', VATICIndexView.as_view(), name='vatic'),
    path('vatic/getjob/', VATICJobView.as_view(), name='vatic_getjob'),
    path('vatic/getboxesforjob/', VATICBoxesForJobView.as_view(), name='vatic_getboxesforjob'),
    path('vatic/validatejob/', VATICValidateJobView.as_view(), name='vatic_validatejob'),
    path('vatic/savejob/', VATICSaveJobView.as_view(), name='vatic_savejob'),
    path('vatic/list/', VATICListView.as_view(), name='vatic_list')
]