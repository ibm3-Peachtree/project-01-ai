# 1. AI 모델 가동을 위해 CUDA가 포함된 이미지를 사용하거나, 경량화가 우선이면 slim 사용
FROM python:3.10-slim

WORKDIR /app

# 2. 시스템 의존성 설치 (불필요한 캐시 삭제 포함)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3. requirements.txt를 먼저 복사하여 종속성 캐싱 활용
COPY requirements.txt .

# 4. pip 설치 최적화
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 복사
COPY . .

# 6. 실행 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]