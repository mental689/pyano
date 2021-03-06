from django.urls import path
from . import views
from pyano2.class_views.keyword_search import KeywordSearchView
from pyano2.class_views.index import IndexView
# from pyano2.class_views.about import Aboutview
from pyano2.class_views.invitation import InvitationView, AcceptInvitationView, DeclineInvitationView, AlternativeRecommendationView
from pyano2.class_views.vatic import VATICIndexView, VATICJobView, VATICBoxesForJobView, \
    VATICValidateJobView, VATICSaveJobView, VATICListView, VATICBidJobView, VATICListJobApplicationView, \
    VATICApproveBidView, VATICFinalizeJobView, VATICCrawlerView, VideoAnswerView, VATICAssignWorker, VATICAssignmentView, CommentView
from pyano2.class_views.qbe_search import QBEVideoSearchView
from pyano2.class_views.lock_channel import LockChannelView


urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    # path('about/', Aboutview.as_view(), name='about'),
    path('keyword_search/', KeywordSearchView.as_view(), name="keyword_search"),
    path('qbe_search/', QBEVideoSearchView.as_view(), name='qbe_search'),
    path('invite/', InvitationView.as_view(), name="invitation"),
    path('accept/', AcceptInvitationView.as_view(), name="accept_invitation"),
    path('decline/', DeclineInvitationView.as_view(), name='decline_invitation'),
    path('recommend_after_decline/', AlternativeRecommendationView.as_view(), name='recommend_alternatives'),
    path('vatic', VATICIndexView.as_view(), name='vatic'),
    path('vatic/getjob/', VATICJobView.as_view(), name='vatic_getjob'),
    path('vatic/getboxesforjob/', VATICBoxesForJobView.as_view(), name='vatic_getboxesforjob'),
    path('vatic/validatejob/', VATICValidateJobView.as_view(), name='vatic_validatejob'),
    path('vatic/savejob/', VATICSaveJobView.as_view(), name='vatic_savejob'),
    path('vatic/list/', VATICListView.as_view(), name='vatic_list'),
    path('vatic/bid/', VATICBidJobView.as_view(), name='vatic_bid'),
    path('vatic/job_applications/', VATICListJobApplicationView.as_view(), name='vatic_applications'),
    path('vatic/approve_bid/', VATICApproveBidView.as_view(), name='vatic_approve_bid'),
    path('vatic/finalize/', VATICFinalizeJobView.as_view(), name='vatic_finalize'),
    path('vatic/crawler/', VATICCrawlerView.as_view(), name='vatic_crawler'),
    path('vatic/assign/', VATICAssignWorker.as_view(), name='vatic_assign'),
    path('vatic/assignment/', VATICAssignmentView.as_view(), name='vatic_assignment_list'),
    path('video/answer/<int:vid>/', VideoAnswerView.as_view(), name='video_answer'),
    path('channel/block/', LockChannelView.as_view(), name='lock_channel'),
    path('vatic/comment/', CommentView.as_view(), name='peer_reviews')
]
