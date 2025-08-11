from pydantic import BaseModel, Field
from typing import List, Optional

class StartSessionRequest(BaseModel):
    student_id: str = Field(..., example="student_123")
    language: str = Field(..., example="en")
    tier: str = Field(..., example="basic")

class StartSessionResponse(BaseModel):
    session_id: str
    message: str

class StepRequest(BaseModel):
    session_id: str = Field(..., example="6ab0b5ac-9d4c-11ec-b909-0242ac120002")
    input_text: str = Field(..., example="I want to become a data scientist")

class Domain(BaseModel):
    title: str
    description: str

class StepResponse(BaseModel):
    prompt: Optional[str] = None
    matching_domains: Optional[List[Domain]] = None
    message: Optional[str] = None
    step: int