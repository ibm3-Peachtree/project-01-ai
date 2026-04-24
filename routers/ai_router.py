from fastapi import APIRouter
from schemas.faq import *
from services.rag_service import rag_service_instance

router = APIRouter(prefix="/api/v0/ai")

@router.post("/faq_generate/{faq_id}", response_model=FAQResponse)
async def generate_answer(faq_id : int, request_data : FAQCreateRequest) :
    # 1. RAG 서비스로 답변 생성
    print(request_data)
    # answer_text = rag_service_instance.generate_answer(request_data.topic, request_data.context)
    
    # 2. 생성된 답변을 Spring Boot DB 저장 API로 전송 (Webhook 응답)
    # Spring Boot에 이 엔드포인트가 미리 만들어져 있어야 합니다.
    # spring_boot_save_url = "http://your-spring-boot-server:8080/api/faq/save-answer"
    
    # async with httpx.AsyncClient() as client:
    #     payload = {
    #         "question_id": faq_id,
    #         "comment": answer_text
    #     }
    #     # 스프링 부트로 답변 전송
    #     response = await client.post(spring_boot_save_url, json=payload)
    
    return {
        "question_id": faq_id,
        "user_id": 1,
        "comment": answer_text,
        # "status": "success" if response.status_code == 200 else "failed"
    }

@router.post("/sync-rag")
async def sync_rag(data : FAQData) :
    rag_service_instance.add_document(data)
    return {"message" : "RAG updated successfully"}