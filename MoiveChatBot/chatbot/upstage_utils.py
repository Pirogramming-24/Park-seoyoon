import os
import math
import requests
from django.conf import settings
from movies.models import Movie
from .models import MovieEmbedding

UPSTAGE_BASE_URL = "https://api.upstage.ai/v1"  # :contentReference[oaicite:1]{index=1}

# 임베딩 모델(문서/질문 분리 권장) :contentReference[oaicite:2]{index=2}
EMBED_QUERY_MODEL = "solar-embedding-1-large-query"
EMBED_PASSAGE_MODEL = "solar-embedding-1-large-passage"

CHAT_MODEL = "solar-1-mini-chat"  # 예시로 많이 사용됨 :contentReference[oaicite:3]{index=3}


def _get_upstage_key() -> str:
    key = getattr(settings, "UPSTAGE_API_KEY", None) or os.getenv("UPSTAGE_API_KEY")
    if not key:
        raise RuntimeError("UPSTAGE_API_KEY가 없습니다. .env 또는 settings에 추가하세요.")
    return key


def movie_to_text(movie: Movie) -> str:
    # 검색 품질을 위해 필드들을 한 문서로 합침
    return (
        f"제목: {movie.title}\n"
        f"개봉년도: {movie.release_year}\n"
        f"장르: {movie.genre}\n"
        f"감독: {movie.director or '-'}\n"
        f"배우: {movie.actors or '-'}\n"
        f"러닝타임: {movie.runtime or '-'}\n"
        f"별점: {movie.rating}\n"
        f"리뷰: {movie.review or '-'}\n"
        f"TMDB: {movie.is_tmdb}\n"
    )


def upstage_embed(text: str, model: str) -> list[float]:
    url = f"{UPSTAGE_BASE_URL}/embeddings"  # :contentReference[oaicite:4]{index=4}
    headers = {
        "Authorization": f"Bearer {_get_upstage_key()}",
        "Content-Type": "application/json",
    }
    payload = {"model": model, "input": text}
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    # OpenAI 스타일: data[0].embedding
    return data["data"][0]["embedding"]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    # 순수 파이썬 코사인 유사도(NumPy 없이)
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def build_or_update_movie_embedding(movie: Movie) -> None:
    text = movie_to_text(movie)
    vec = upstage_embed(text, model=EMBED_PASSAGE_MODEL)
    MovieEmbedding.objects.update_or_create(movie=movie, defaults={"vector": vec})


def retrieve_top_k_movies(query: str, k: int = 5) -> list[tuple[Movie, float]]:
    qvec = upstage_embed(query, model=EMBED_QUERY_MODEL)

    scored: list[tuple[Movie, float]] = []
    qs = MovieEmbedding.objects.select_related("movie").all()

    for emb in qs:
        sim = cosine_similarity(qvec, emb.vector)
        scored.append((emb.movie, sim))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]


def upstage_chat(system: str, user: str) -> str:
    url = f"{UPSTAGE_BASE_URL}/chat/completions"  # :contentReference[oaicite:5]{index=5}
    headers = {
        "Authorization": f"Bearer {_get_upstage_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.3,
        "max_tokens": 800,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]
