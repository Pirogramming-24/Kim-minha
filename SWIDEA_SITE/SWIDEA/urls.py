from django.urls import path
from . import views

app_name = "swidea"

urlpatterns = [
    path("", views.idea_list, name="idea_list"),
    path("idea/create/", views.idea_create, name="idea_create"),
    path("idea/<int:pk>/", views.idea_detail, name="idea_detail"),
    path("idea/<int:pk>/update/", views.idea_update, name="idea_update"),
    path("idea/<int:pk>/delete/", views.idea_delete, name="idea_delete"),
    path("idea/<int:pk>/star/", views.idea_toggle_star, name="idea_star"),

    path("idea/<int:pk>/interest/plus/", views.idea_interest_plus, name="idea_interest_plus"),
    path("idea/<int:pk>/interest/minus/", views.idea_interest_minus, name="idea_interest_minus"),

    path("devtool/", views.devtool_list, name="devtool_list"),
    path("devtool/create/", views.devtool_create, name="devtool_create"),
    path("devtool/<int:pk>/", views.devtool_detail, name="devtool_detail"),
    path("devtool/<int:pk>/update/", views.devtool_update, name="devtool_update"),
    path("devtool/<int:pk>/delete/", views.devtool_delete, name="devtool_delete"),
]
