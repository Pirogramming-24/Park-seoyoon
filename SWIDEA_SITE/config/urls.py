"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect #바로 들어가게 됨 

urlpatterns = [
    path("", lambda request: redirect("ideaapp:idea_list"), name="home"),
    path('admin/', admin.site.urls), #이거로 가면 관리자페이지가 열림 
    path("", include("ideaapp.urls")),#/로 시작하는 모든 요청은 ideaapp 한테 맡긴다. 
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
