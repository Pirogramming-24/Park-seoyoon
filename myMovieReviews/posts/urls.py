# posts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_list, name='review_list'),                 # /posts/
    path('create/', views.review_create, name='review_create'),      # /posts/create/
    path('<int:pk>/', views.review_detail, name='review_detail'),    # /posts/3/
    path('<int:pk>/update/', views.review_update, name='review_update'), # /posts/3/update/
    path('<int:pk>/delete/', views.review_delete, name='review_delete'), # /posts/3/delete/
]
