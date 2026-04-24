# 1. Python 3.10 공식 이미지 사용
FROM python:3.10-slim

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. requirements.txt 먼저 복사 (캐시 최적화)
COPY requirements.txt .

# 4. pip 업그레이드 + 의존성 설치
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 복사
COPY . .

# 6. FastAPI 실행 포트
EXPOSE 8000

# 7️⃣ 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]