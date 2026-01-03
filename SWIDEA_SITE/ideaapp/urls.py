from django.urls import path
from . import views

app_name = "ideaapp"

urlpatterns = [
    # Idea
    path("ideas/", views.idea_list, name="idea_list"),
    path("ideas/create/", views.idea_create, name="idea_create"),
    path("ideas/<int:pk>/", views.idea_detail, name="idea_detail"),
    path("ideas/<int:pk>/edit/", views.idea_edit, name="idea_edit"),
    path("ideas/<int:pk>/delete/", views.idea_delete, name="idea_delete"),

    # DevTool
    path("devtools/", views.devtool_list, name="devtool_list"),
    path("devtools/create/", views.devtool_create, name="devtool_create"),
    path("devtools/<int:pk>/", views.devtool_detail, name="devtool_detail"),#상세페이지
    path("devtools/<int:pk>/edit/", views.devtool_edit, name="devtool_edit"),#수정
    path("devtools/<int:pk>/delete/", views.devtool_delete, name="devtool_delete"), #삭제 

    path("ideas/<int:pk>/toggle_star/", views.toggle_star, name="toggle_star"),
    path("ideas/<int:pk>/interest/<str:action>/", views.update_interest, name="update_interest"),


]

