from django.urls import path
from . import views

urlpatterns = [
    path('', views.community, name="community"),
    path('post/<str:pk>/', views.post, name="post"),
    path('create-post/', views.createPost, name="create-post"),
    path('update-post/<str:pk>/', views.updatePost, name="update-post"),
    path('delete-post/<str:pk>/', views.deletePost, name="delete-post"),
    path('delete-comment/<str:pk>/', views.deleteComment, name="delete-comment"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),
    path('topics/', views.topicsPage, name="topics"),
    path('activity/', views.activityPage, name="activity"),
    path('update-user/', views.updateUser, name="update-user"),
]