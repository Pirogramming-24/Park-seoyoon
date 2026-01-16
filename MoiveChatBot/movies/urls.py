# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.movie_list, name='movie_list'),
#     # path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
#     # path('movie/create/', views.movie_create, name='movie_create'),
#     # path('movie/<int:pk>/update/', views.movie_update, name='movie_update'),
#     # path('movie/<int:pk>/delete/', views.movie_delete, name='movie_delete'),
#     # path('fetch-tmdb/', views.fetch_tmdb_movies, name='fetch_tmdb'),
#     # path('chatbot/', views.chatbot, name='chatbot'),
#     # path('chatbot/response/', views.chatbot_response, name='chatbot_response'),
# ]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),

    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('movie/create/', views.movie_create, name='movie_create'),
    path('movie/<int:pk>/update/', views.movie_update, name='movie_update'),
    path('movie/<int:pk>/delete/', views.movie_delete, name='movie_delete'),
    #path('fetch-tmdb/', views.fetch_tmdb_movies, name='fetch_tmdb'),

]
