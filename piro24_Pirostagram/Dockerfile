# syntax=docker/dockerfile:1

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Pillow 등 이미지 라이브러리 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) 현재 폴더의 requirements.txt를 컨테이너 안으로 복사
# (현재 Dockerfile과 같은 위치에 있으므로 경로 수정)
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# 2) 현재 폴더의 모든 소스 코드(manage.py 등)를 컨테이너 안으로 복사
# (현재 구조에 맞춰 ./ 에서 ./ 로 복사)
COPY . /app/

# 3) 정적 파일 수집 (STATIC_ROOT 설정이 되어 있어야 함)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# 4) 실행 명령 (config 폴더 안의 wsgi.py를 통해 실행)
# 만약 gunicorn 설치가 안 되어 있다면 pip install gunicorn을 하거나 
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 로 변경하세요.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]