from django.urls import path
from .views import *

app_name = 'posts'

urlpatterns = [
    path('', main, name='main'),
    path('create', create, name='create'),
    path('detail/<int:pk>', detail, name='detail'),
    path('update/<int:pk>', update, name='update'),
    path('delete/<int:pk>', delete, name='delete'),
]