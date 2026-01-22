# accounts/views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count, Q
from django.utils import timezone
from posts.models import Post
from stories.models import Story
from .models import Follow

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect("posts:feed")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("posts:feed")
        error = "아이디 또는 비밀번호가 올바르지 않습니다."

    return render(request, "accounts/login.html", {"error": error})

def logout_view(request):
    # GET으로도 로그아웃 되게 처리(학습/과제 편의)
    logout(request)
    return redirect("posts:feed")

def search(request):
    q = request.GET.get("q", "").strip()
    tab = request.GET.get("tab", "posts")   # posts | users
    sort = request.GET.get("sort", "new")   # new | likes | comments

    users = User.objects.none()
    posts = Post.objects.none()
    stories = Story.objects.none()

    if q:
        # ✅ 유저 검색
        users = User.objects.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        ).order_by("username")[:30]

        # ✅ 게시글 검색 (내용 + 작성자 username)
        post_qs = Post.objects.select_related("author").annotate(
            like_count=Count("likes"),
            comment_count=Count("comments"),
        ).filter(
            Q(content__icontains=q) |
            Q(author__username__icontains=q)
        )

        # ✅ 로그인 시: 팔로잉+나만 보이게(요구사항 일관성)
        if request.user.is_authenticated:
            following_ids = Follow.objects.filter(
                follower=request.user
            ).values_list("following_id", flat=True)

            allowed_author_ids = list(following_ids) + [request.user.id]
            post_qs = post_qs.filter(author_id__in=allowed_author_ids)

            stories = Story.objects.select_related("author").filter(
                expires_at__gt=timezone.now(),
                author_id__in=allowed_author_ids
            ).order_by("-created_at")

        # ✅ 정렬
        if sort == "likes":
            post_qs = post_qs.order_by("-like_count", "-created_at")
        elif sort == "comments":
            post_qs = post_qs.order_by("-comment_count", "-created_at")
        else:
            post_qs = post_qs.order_by("-created_at")

        posts = post_qs

    return render(
        request,
        "accounts/search_results.html",
        {
            "q": q,
            "tab": tab,
            "sort": sort,
            "users": users,
            "posts": posts,
            "stories": stories,  # 검색 결과 페이지에서도 스토리바 보이게 하고 싶으면 활용
        },
    )


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    is_following = False
    if request.user.is_authenticated and request.user.id != profile_user.id:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()

    follower_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": profile_user,
            "is_following": is_following,
            "follower_count": follower_count,
            "following_count": following_count,
        },
    )

@login_required
def follow_toggle(request, username):
    if request.method != "POST":
        raise Http404()

    target = get_object_or_404(User, username=username)

    if target.id == request.user.id:
        # 자기 자신 팔로우 방지
        return redirect("accounts:profile", username=username)

    rel = Follow.objects.filter(follower=request.user, following=target)
    if rel.exists():
        rel.delete()
    else:
        Follow.objects.create(follower=request.user, following=target)

    return redirect("accounts:profile", username=username)
