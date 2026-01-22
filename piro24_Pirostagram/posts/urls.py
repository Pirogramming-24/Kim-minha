from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path("", views.FeedView.as_view(), name="feed"),
    path("posts/new/", views.PostCreateView.as_view(), name="create"),
    path("posts/<int:pk>/edit/", views.PostUpdateView.as_view(), name="update"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="delete"),

    path("posts/<int:pk>/", views.post_detail, name="detail"),
    path("posts/<int:pk>/like/", views.like_toggle, name="like_toggle"),

    path("posts/<int:pk>/comments/new/", views.comment_create, name="comment_create"),
    path("comments/<int:comment_id>/edit/", views.comment_update, name="comment_update"),
    path("comments/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),

    path("users/<str:username>/", views.profile_view, name="profile"),
    path("users/<str:username>/follow/", views.follow_toggle, name="follow_toggle"),
    path("search/users/", views.user_search, name="user_search"),

    path("stories/new/", views.story_create, name="story_create"),
    path("stories/<int:story_id>/", views.story_view, name="story_view"),
]
