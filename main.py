from fastapi import FastAPI
from routers import ai_router
<<<<<<< HEAD

API_PREFIX = "/api/v0/ai"
=======
import config
>>>>>>> 8404d7a06383f56cdf512e37478e94f83af1ce05

app = FastAPI(
    title="AI Service API",
    description="AI 생성을 위한 API 서버",
    version="1.0.0",
    docs_url=config.API_PREFIX + "/docs", 
    openapi_url=config.API_PREFIX + "/openapi.json"
)

app.include_router(ai_router.router)

if __name__ == "__main__" :
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)