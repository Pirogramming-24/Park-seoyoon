from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.conf import settings
from django.core.paginator import Paginator
import requests

from .models import Movie
from .forms import MovieForm
from chatbot.upstage_utils import build_or_update_movie_embedding
from chatbot.models import MovieEmbedding


# TMDB genre_id -> 네 GENRE_CHOICES 텍스트로 간단 매핑
TMDB_GENRE_MAP = {
    28: "액션",
    35: "코미디",
    18: "드라마",
    27: "공포",
    878: "SF",
    10749: "로맨스",
    53: "스릴러",
    16: "애니메이션",
    14: "판타지",
    99: "다큐멘터리",
}


def _pick_genre_from_tmdb(genre_ids):
    """TMDB genre_ids(list)에서 가장 앞의 매핑 가능한 장르 하나 선택"""
    if not genre_ids:
        return "드라마"
    for gid in genre_ids:
        if gid in TMDB_GENRE_MAP:
            return TMDB_GENRE_MAP[gid]
    return "드라마"


def _sync_tmdb_popular_if_empty():
    """
    DB에 영화가 0개일 때만 TMDB 인기영화를 가져와 저장.
    (서버/페이지 접속 시 자동 1회 채우기용)
    """
    if Movie.objects.exists():
        return 0

    api_key = getattr(settings, "TMDB_API_KEY", None)
    if not api_key:
        return 0

    url = "https://api.themoviedb.org/3/movie/popular"
    params = {"api_key": api_key, "language": "ko-KR", "page": 1}

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    saved = 0
    for item in data.get("results", []):
        tmdb_id = item.get("id")
        title = item.get("title") or ""
        release_date = item.get("release_date") or ""
        year = int(release_date[:4]) if release_date[:4].isdigit() else 2000

        poster_path = item.get("poster_path") or ""
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

        genre = _pick_genre_from_tmdb(item.get("genre_ids", []))

        # 이미 tmdb_id가 있으면 업데이트, 없으면 생성
        Movie.objects.update_or_create(
            tmdb_id=tmdb_id,
            defaults={
                "title": title,
                "release_year": year,
                "genre": genre,
                "poster_url": poster_url,
                "is_tmdb": True,
            },
        )
        saved += 1

    return saved


def movie_list(request):
    """영화 목록 페이지 (메인)"""
    # ✅ DB가 비어있을 때만 TMDB에서 자동으로 채우기
    _sync_tmdb_popular_if_empty()

    movies = Movie.objects.all()

    # 검색
    search_query = request.GET.get("search", "")
    if search_query:
        movies = movies.filter(
            Q(title__icontains=search_query)
            | Q(director__icontains=search_query)
            | Q(actors__icontains=search_query)
        )

    # 필터 (전체, TMDB, 직접추가)
    filter_type = request.GET.get("filter", "all")
    if filter_type == "tmdb":
        movies = movies.filter(is_tmdb=True)
    elif filter_type == "user":
        movies = movies.filter(is_tmdb=False)

    # 정렬
    sort_by = request.GET.get("sort", "latest")
    if sort_by == "latest":
        movies = movies.order_by("-created_at")
    elif sort_by == "title":
        movies = movies.order_by("title")
    elif sort_by == "rating":
        movies = movies.order_by("-rating")
    elif sort_by == "year":
        movies = movies.order_by("-release_year")

    # 통계
    total_count = Movie.objects.count()
    tmdb_count = Movie.objects.filter(is_tmdb=True).count()
    user_count = Movie.objects.filter(is_tmdb=False).count()

    # 페이지네이션
    paginator = Paginator(movies, 12)
    page = request.GET.get("page", 1)
    movies = paginator.get_page(page)

    context = {
        "movies": movies,
        "search_query": search_query,
        "filter_type": filter_type,
        "sort_by": sort_by,
        "total_count": total_count,
        "tmdb_count": tmdb_count,
        "user_count": user_count,
    }
    return render(request, "movies/movie_list.html", context)


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    prev_movie = Movie.objects.filter(pk__lt=movie.pk).order_by("-pk").first()
    next_movie = Movie.objects.filter(pk__gt=movie.pk).order_by("pk").first()

    return render(
        request,
        "movies/movie_detail.html",
        {
            "movie": movie,
            "prev_movie": prev_movie,
            "next_movie": next_movie,
        },
    )



def movie_create(request):
    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save(commit=False)
            movie.is_tmdb = False  # 직접 입력
            movie.save()

            # ✅ 여기서 임베딩 생성/갱신
            build_or_update_movie_embedding(movie)

            return redirect("movie_detail", pk=movie.pk)
    else:
        form = MovieForm()

    return render(request, "movies/movie_form.html", {"form": form, "mode": "create"})


def movie_update(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES, instance=movie)
        if form.is_valid():
            movie = form.save()
            build_or_update_movie_embedding(movie)
            return redirect("movie_detail", pk=movie.pk)
    else:
        form = MovieForm(instance=movie)

    return render(request, "movies/movie_form.html", {"form": form, "movie": movie, "mode": "update"})


def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        MovieEmbedding.objects.filter(movie=movie).delete()
        movie.delete()
        return redirect("movie_list")
    return render(request, "movies/movie_confirm_delete.html", {"movie": movie})
