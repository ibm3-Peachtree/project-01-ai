from pydantic import BaseModel, Field
from typing import Optional

class FAQCreateRequest(BaseModel) :
    title : str = Field(..., description="FAQ 제목")
    content : str = Field(..., description="FAQ 내용")

class FAQResponse(BaseModel) :
    question_id : int
    comment : str
    status : Optional[str] = "success"

class FAQData(BaseModel) :
    notice_id : int
    title : str
    content : str