from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ai_router
import config

app = FastAPI(
    title="AI Service API",
    description="AI 생성을 위한 API 서버",
    version="1.0.0",
    docs_url=config.API_PREFIX + "/docs", 
    openapi_url=config.API_PREFIX + "/openapi.json"
)

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    # 허용할 도메인 (프론트엔드 주소)
    allow_origins=["http://192.168.0.79"], 
    # 쿠키나 인증 정보를 포함할지 여부
    allow_credentials=True, 
    # 허용할 HTTP 메서드
    allow_methods=["*"], 
    # 허용할 HTTP 헤더
    allow_headers=["*"],
)

app.include_router(ai_router.router)

if __name__ == "__main__" :
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)