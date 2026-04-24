import os
from fastapi import APIRouter
import httpx
from fastapi import Header, HTTPException, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from dotenv import load_dotenv

import config
from schemas.faq import *
from schemas.summary import *
from services.ai_service import rag_service_instance, sum_service_instance

router = APIRouter(prefix=config.API_PREFIX)

# Security
security = HTTPBearer()
load_dotenv()
def verify_internal_request(x_internal_secret: str = Header(...)):
    if x_internal_secret != os.getenv("INTERNAL_SECRET"):
        raise HTTPException(status_code=403, detail="권한이 없습니다.")

def get_admin_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    secret_key = config.JWT_SECRET_KEY
    if secret_key is None:
        raise HTTPException(status_code=500, detail="서버 설정 오류: JWT_SECRET_KEY가 없습니다.")
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        # 1. payload 전체와 role 값 디버깅 출력
        role = payload.get("role")
        print(f"DEBUG: JWT Payload: {payload}")
        print(f"DEBUG: Extracted Role: {role} (Type: {type(role)})")
        
        # 2. 역할 확인 로직 (문자열인 경우와 리스트인 경우 모두 대응)
        is_admin = False
        if isinstance(role, str):
            is_admin = role.lower() == "role_admin"
        elif isinstance(role, list):
            is_admin = any(r.lower() == "role_admin" for r in role)
            
        if not is_admin:
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        return payload
    except JWTError as e:
        print(f"DEBUG: JWT Error: {e}")
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 토큰입니다.")

# API
@router.post("/sync-rag", dependencies=[Depends(verify_internal_request)])
async def sync_rag(data : FAQData) :
    # print("sync_rag 접속 성공")
    rag_service_instance.add_document(data)
    return {"message" : "RAG updated successfully"}

@router.post("/faq_generate/{faq_id}", response_model=FAQResponse, dependencies=[Depends(verify_internal_request)])
async def generate_answer(faq_id : int, data : FAQCreateRequest) :
    # print("generate_answer 접속 성공")
    # 1. RAG 서비스로 답변 생성
    answer_text = rag_service_instance.generate_answer(data)
    
    # 2. 생성된 답변을 Spring Boot DB 저장 API로 전송 (Webhook 응답)
    # Spring Boot에 이 엔드포인트가 미리 만들어져 있어야 합니다.
    spring_boot_save_url = "http://localhost:8080/api/v0/supports/faq/ans/save-answer"
    payload = {
            "question_id": faq_id,
            "comment": answer_text
    }
    async with httpx.AsyncClient() as client:
        try :
            # 스프링 부트로 답변 전송
            response = await client.post(spring_boot_save_url, json=payload, timeout=60)
        except Exception as e :
            print(f"Spring Boot 웹훅 전송 실패: {e}")
    
    return {
        "question_id": faq_id,
        "comment": answer_text,
        "status": "success" if response.status_code == 200 else "failed"
    }

@router.post("/summarize_session")
async def summarize_session(
    data : SummaryCreateRequest,
    admin_info: dict = Depends(get_admin_user)
) :
    response = sum_service_instance.summarize_session(data)

    return {
        "summary" : response
    }