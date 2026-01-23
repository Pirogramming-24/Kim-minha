# 1. 파이썬 3.12 버전을 기반으로 시작
FROM python:3.12

# 2. 파이썬 출력을 버퍼링 없이 즉시 보여주게 설정 (로그 확인용)
ENV PYTHONUNBUFFERED=1

# 3. 도커 안의 작업 폴더를 /app으로 설정
WORKDIR /app

# 4. 필요한 패키지 리스트 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 현재 폴더의 모든 파일을 도커 내부로 복사
COPY . .

# 6. 서버 실행 명령어 (0.0.0.0으로 열어야 외부 접속 가능)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]