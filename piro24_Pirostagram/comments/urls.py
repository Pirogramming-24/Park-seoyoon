# comments/urls.py
from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    # ✅ 특정 게시글의 댓글 페이지(전체 CRUD)
    path("<int:post_id>/", views.post_comments, name="post_comments"),

    # ✅ 댓글 삭제/수정 액션(댓글 페이지에서 POST로 호출)
    path("<int:post_id>/delete/<int:comment_id>/", views.comment_delete, name="delete"),
    path("<int:post_id>/edit/<int:comment_id>/", views.comment_update, name="update"),
    path("<int:post_id>/reply/<int:comment_id>/create/", views.reply_create, name="reply_create"),
    path("<int:post_id>/reply/<int:comment_id>/edit/<int:reply_id>/", views.reply_update, name="reply_update"),
    path("<int:post_id>/reply/<int:comment_id>/delete/<int:reply_id>/", views.reply_delete, name="reply_delete"),

]
