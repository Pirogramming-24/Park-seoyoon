from django.db import models
from movies.models import Movie


class MovieEmbedding(models.Model):
    """
    영화 하나당 하나의 임베딩 벡터를 저장
    (RAG 검색용)
    """
    movie = models.OneToOneField(
        Movie,
        on_delete=models.CASCADE,
        related_name="embedding"
    )
    vector = models.JSONField()  # list[float]
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Embedding(movie_id={self.movie.id}, title={self.movie.title})"
