# comments/views.py
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from posts.models import Post
from .models import Comment, Reply
from .forms import CommentForm, ReplyForm


def post_comments(request, post_id):
    """
    /comments/<post_id>/
    GET  : 댓글/대댓글 전체 렌더
    POST : 새 댓글 작성
    """
    post = get_object_or_404(Post.objects.select_related("author"), id=post_id)

    comments = (
        Comment.objects
        .filter(post=post)
        .select_related("author")
        .prefetch_related("replies", "replies__author")
        .order_by("created_at")
    )

    edit_id = request.GET.get("edit")          # 댓글 인라인 수정: ?edit=comment_id
    reply_to = request.GET.get("reply_to")     # 대댓글 입력폼 열기: ?reply_to=comment_id
    reply_edit = request.GET.get("reply_edit") # 대댓글 수정폼 열기: ?reply_edit=reply_id

    # 댓글 작성(POST)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.post = post
            c.author = request.user
            c.save()
            return redirect("comments:post_comments", post_id=post_id)
    else:
        form = CommentForm()

    # 댓글 수정용 폼 준비
    edit_form = None
    edit_comment = None
    if edit_id:
        try:
            edit_id_int = int(edit_id)
        except ValueError:
            edit_id_int = None

        if edit_id_int:
            edit_comment = get_object_or_404(Comment, id=edit_id_int, post=post)
            if request.user.is_authenticated and edit_comment.author_id == request.user.id:
                edit_form = CommentForm(instance=edit_comment)

    # 대댓글 작성 폼 준비(특정 comment에만)
    reply_form = None
    reply_target_comment_id = None
    if reply_to:
        try:
            reply_target_comment_id = int(reply_to)
        except ValueError:
            reply_target_comment_id = None

        if reply_target_comment_id:
            # 댓글 존재 확인
            _ = get_object_or_404(Comment, id=reply_target_comment_id, post=post)
            reply_form = ReplyForm()

    # 대댓글 수정 폼 준비(특정 reply에만)
    reply_edit_form = None
    reply_edit_obj = None
    if reply_edit:
        try:
            reply_edit_int = int(reply_edit)
        except ValueError:
            reply_edit_int = None

        if reply_edit_int:
            reply_edit_obj = get_object_or_404(Reply, id=reply_edit_int, comment__post=post)
            if request.user.is_authenticated and reply_edit_obj.author_id == request.user.id:
                reply_edit_form = ReplyForm(instance=reply_edit_obj)

    return render(
        request,
        "comments/post_comments.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "edit_comment": edit_comment,
            "edit_form": edit_form,
            "reply_form": reply_form,
            "reply_target_comment_id": reply_target_comment_id,
            "reply_edit_obj": reply_edit_obj,
            "reply_edit_form": reply_edit_form,
        },
    )


@login_required
@require_POST
def comment_delete(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)

    if comment.author_id != request.user.id:
        raise Http404("권한이 없습니다.")

    comment.delete()
    return redirect("comments:post_comments", post_id=post_id)


@login_required
@require_POST
def comment_update(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)

    if comment.author_id != request.user.id:
        raise Http404("권한이 없습니다.")

    form = CommentForm(request.POST, instance=comment)
    if form.is_valid():
        form.save()

    return redirect("comments:post_comments", post_id=post_id)


# =========================
# ✅ Reply CRUD
# =========================
@login_required
@require_POST
def reply_create(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)

    form = ReplyForm(request.POST)
    if form.is_valid():
        r = form.save(commit=False)
        r.comment = comment
        r.author = request.user
        r.save()

    return redirect("comments:post_comments", post_id=post_id)


@login_required
@require_POST
def reply_delete(request, post_id, comment_id, reply_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)
    reply = get_object_or_404(Reply, id=reply_id, comment=comment)

    if reply.author_id != request.user.id:
        raise Http404("권한이 없습니다.")

    reply.delete()
    return redirect("comments:post_comments", post_id=post_id)


@login_required
@require_POST
def reply_update(request, post_id, comment_id, reply_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)
    reply = get_object_or_404(Reply, id=reply_id, comment=comment)

    if reply.author_id != request.user.id:
        raise Http404("권한이 없습니다.")

    form = ReplyForm(request.POST, instance=reply)
    if form.is_valid():
        form.save()

    return redirect("comments:post_comments", post_id=post_id)
