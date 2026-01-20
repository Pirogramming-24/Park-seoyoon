from django.db import models
from django.conf import settings
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
import requests

class Movie(models.Model):
    GENRE_CHOICES = [
        ('액션', '액션'),
        ('코미디', '코미디'),
        ('드라마', '드라마'),
        ('공포', '공포'),
        ('SF', 'SF'),
        ('로맨스', '로맨스'),
        ('스릴러', '스릴러'),
        ('애니메이션', '애니메이션'),
        ('판타지', '판타지'),
        ('다큐멘터리', '다큐멘터리'),
    ]
    
    RATING_CHOICES = [(i, f'{i}점') for i in range(1, 6)]
    
    title = models.CharField(max_length=200, verbose_name='영화 제목')
    release_year = models.IntegerField(verbose_name='개봉 년도')
    director = models.CharField(max_length=100, blank=True, verbose_name='감독')
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, verbose_name='장르')
    actors = models.CharField(max_length=500, blank=True, verbose_name='주연배우')
    runtime = models.IntegerField(null=True, blank=True, verbose_name='러닝타임(분)')
    rating = models.IntegerField(choices=RATING_CHOICES, default=3, verbose_name='별점')
    review = models.TextField(blank=True, verbose_name='리뷰 내용')
    poster = models.ImageField(upload_to='posters/', blank=True, null=True, verbose_name='포스터 이미지')
    poster_url = models.URLField(blank=True, verbose_name='포스터 URL')
    tmdb_id = models.IntegerField(null=True, blank=True, unique=True, verbose_name='TMDB ID')
    is_tmdb = models.BooleanField(default=False, verbose_name='TMDB 데이터')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '영화'
        verbose_name_plural = '영화들'
    
    def __str__(self):
        return self.title
    
    def get_poster_display(self):
        """포스터 이미지 URL 반환 (업로드 이미지 또는 TMDB URL)"""
        if self.poster:
            return self.poster.url
        elif self.poster_url:
            return self.poster_url
        return '/static/images/no-poster.png'
    
    def get_star_rating(self):
        """별점을 별 아이콘으로 반환"""
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    def get_runtime_display(self):
        """러닝타임을 시간:분 형식으로 반환"""
        if self.runtime:
            hours = self.runtime // 60
            minutes = self.runtime % 60
            if hours > 0:
                return f'{hours}시간 {minutes}분'
            return f'{minutes}분'
        return '정보 없음'

@require_POST
def fetch_tmdb_movies(request):
    api_key = getattr(settings, "TMDB_API_KEY", None)
    if not api_key:
        # settings에 키가 없으면 아무것도 안 함(또는 에러 처리)
        return redirect("movie_list")

    url = "https://api.themoviedb.org/3/movie/popular"
    params = {"api_key": api_key, "language": "ko-KR", "page": 1}
    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    results = data.get("results", [])
    for item in results:
        tmdb_id = item.get("id")
        title = item.get("title") or ""
        release_date = item.get("release_date") or ""
        year = int(release_date[:4]) if release_date[:4].isdigit() else 0
        poster_path = item.get("poster_path") or ""
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

        # TMDB는 장르명 대신 genre_ids를 주는 경우가 많아서, 일단 기본값으로 넣음
        # (원하면 genre 매핑도 추가해줄게)
        genre_default = "드라마"

        Movie.objects.update_or_create(
            tmdb_id=tmdb_id,
            defaults={
                "title": title,
                "release_year": year if year else 2000,  # year 필수라 임시값
                "genre": genre_default,
                "poster_url": poster_url,
                "is_tmdb": True,
            },
        )

    return redirect("movie_list")

