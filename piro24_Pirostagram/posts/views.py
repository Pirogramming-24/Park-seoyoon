# posts/views.py 상단 import 예시
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.utils import timezone
from stories.models import Story

from .models import Post, Like
from .forms import PostForm
from accounts.models import Follow
# posts/views.py (추가 import)




def feed(request):
    qs = Post.objects.select_related("author").prefetch_related(
        "comments",
        "comments__author",
    ).annotate(
        like_count=Count("likes"),
        comment_count=Count("comments"),
    )

    liked_post_ids = set()
    active_stories = Story.objects.none()

    if request.user.is_authenticated:
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list("following_id", flat=True)

        allowed_author_ids = list(following_ids) + [request.user.id]

        # ✅ 팔로잉 + 나의 게시글만
        qs = qs.filter(author_id__in=allowed_author_ids)

        # ✅ 내가 좋아요 누른 게시글 id
        liked_post_ids = set(
            Like.objects.filter(user=request.user).values_list("post_id", flat=True)
        )

        # ✅ 팔로잉 + 나의 스토리만 + 만료 안 된 것만
        active_stories = Story.objects.select_related("author").filter(
            expires_at__gt=timezone.now(),
            author_id__in=allowed_author_ids,
        ).order_by("-created_at")

    posts = qs.order_by("-created_at")

    return render(
        request,
        "posts/feed.html",
        {
            "posts": posts,
            "liked_post_ids": liked_post_ids,
            "stories": active_stories,
        },
    )




@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:feed")
    else:
        form = PostForm()
    return render(request, "posts/post_form.html", {"form": form, "mode": "create"})


@login_required
def post_update(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author_id != request.user.id:
        raise Http404("권한이 없습니다.")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("posts:feed")
    else:
        form = PostForm(instance=post)

    return render(request, "posts/post_form.html", {"form": form, "mode": "update", "post": post})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author_id != request.user.id:
        raise Http404("권한이 없습니다.")

    if request.method == "POST":
        post.delete()
        return redirect("posts:feed")

    return render(request, "posts/post_confirm_delete.html", {"post": post})

from django.views.decorators.http import require_POST

@login_required
@require_POST
def like_toggle(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    like_qs = Like.objects.filter(user=request.user, post=post)
    if like_qs.exists():
        like_qs.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True

    like_count = Like.objects.filter(post=post).count()

    return JsonResponse({
        "post_id": post.id,
        "liked": liked,
        "like_count": like_count,
    })

