from pydantic import BaseModel, Field
from typing import Optional

class SummaryCreateRequest(BaseModel) :
    title : str = Field(..., description="Session 제목")
    content : str = Field(..., description="Session 내용")