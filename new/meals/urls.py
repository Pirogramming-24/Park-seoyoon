from django.urls import path
from .views import *

app_name = 'meals'

urlpatterns = [
    path('', meals_index), #veiw에서 사용하는 이름 
]