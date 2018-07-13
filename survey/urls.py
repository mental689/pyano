from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('job/', views.job, name="job"),
    path('submission/', views.submission, name="submission"),
    path('complete/', views.complete, name="complete"),
    path('review_video/', views.review_video, name="review_video"),
    path('register/', views.register, name="register")
]