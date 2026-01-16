from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.main, name='main'),
    path('create', views.create, name='create'),
    path('detail/<int:pk>', views.detail, name='detail'),
    path('update/<int:pk>', views.update, name='update'),
    path('delete/<int:pk>', views.delete, name='delete'),
    # apps/posts/urls.py
    path('api/analyze-image/', views.api_analyze_image, name='api_analyze_image'),
    path('<int:pk>/analysis-status/', views.get_analysis_status, name='analysis_status'),
    #OCR API 엔드 포인트 작성해야됨
]