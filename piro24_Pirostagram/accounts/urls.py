# accounts/urls.py
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("search/", views.search, name="search"),
    path("<str:username>/", views.profile, name="profile"),
    path("<str:username>/follow/", views.follow_toggle, name="follow_toggle"),
    path("u/<str:username>/", views.profile, name="profile"),
]
