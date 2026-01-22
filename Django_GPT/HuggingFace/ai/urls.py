from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path("", views.home, name = "home"),
    path('generate-text/', views.generate_text_view, name='generate_text'),      # 공개
    path('generate-image/', views.generate_image_view, name='generate_image'),   # 로그인 필요
    path("combo/", views.combo_view, name="combo"),

]