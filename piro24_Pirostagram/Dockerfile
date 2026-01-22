# 1) Python slim 이미지
FROM python:3.12-slim

# 2) 기본 환경 변수
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3) 작업 디렉토리
WORKDIR /app

# 4) 시스템 패키지(이미지 처리용 libjpeg/zlib, 빌드 도구)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 5) requirements 먼저 복사(캐시 효율)
COPY requirements.txt /app/

# 6) pip 설치
RUN pip install --upgrade pip && pip install -r requirements.txt

# 7) 프로젝트 전체 복사
COPY . /app/

# 8) 컨테이너 내부에서 사용할 폴더 보장
RUN mkdir -p /app/staticfiles /app/media

# 9) 포트
EXPOSE 8000

# 10) 실행 커맨드: migrate -> collectstatic -> runserver
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
