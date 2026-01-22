# stories/urls.py
from django.urls import path
from . import views

app_name = "stories"

urlpatterns = [
    path("new/", views.story_create, name="create"),
    path("<int:story_id>/", views.story_view, name="view"),
]
