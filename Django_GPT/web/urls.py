 # cat > 의미: urls에 EOF까지 리다이렉트하기, lilyai의 url에 다 넣으면 길어지니까 파일분리
from django.urls import path
from . import views #. :같은 파일안에 있다는뜻, views.py를 가져오기

urlpatterns = [
    path("", views.home, name="home"),
    path("summarize/", views.summarize, name="summarize"),
    path("translate/", views.translate, name="translate"),
    path("generate/", views.generate, name="generate"),
]
 #파일의 끝이라고 전달해주는거임
