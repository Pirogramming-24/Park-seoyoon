from django.urls import path
from . import views

urlpatterns = [
    path("", views.chatbot_page, name="chatbot"),
    path("response/", views.chatbot_response, name="chatbot_response"),
]
