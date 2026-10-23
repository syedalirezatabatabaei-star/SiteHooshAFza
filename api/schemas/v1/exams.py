from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class ChoiceResponse(BaseModel):
    id: int
    text: str

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: int
    text: str
    score: Decimal
    order: int
    choices: List[ChoiceResponse] = []

    class Config:
        from_attributes = True


class ExamListResponse(BaseModel):
    id: int
    title: str
    description: str = ''
    duration_minutes: int
    passing_score: Decimal
    question_count: int = 0
    course_id: int

    class Config:
        from_attributes = True


class ExamDetailResponse(BaseModel):
    id: int
    title: str
    description: str
    duration_minutes: int
    passing_score: Decimal
    questions: List[QuestionResponse] = []
    total_score: Decimal = 0

    class Config:
        from_attributes = True


class ExamAnswerItem(BaseModel):
    question_id: int
    choice_id: int


class ExamSubmitRequest(BaseModel):
    answers: List[ExamAnswerItem]


class ExamResultResponse(BaseModel):
    score: Decimal
    total_score: Decimal
    passed: bool
    passing_score: Decimal
