from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class Language(str, Enum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    JAPANESE = "ja"

class Tier(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class StepType(str, Enum):
    PROFILE_SETUP = "profile_setup"
    INTERESTS_STRENGTHS = "interests_strengths"
    VALUES_PREFERENCES = "values_preferences"
    LEARNING_PERSONALITY = "learning_personality"
    PASSION_CAREER_FIT = "passion_career_fit"
    COGNITIVE_THINKING = "cognitive_thinking"
    EMOTIONAL_ETHICAL = "emotional_ethical"
    CAREER_SUMMARY = "career_summary"
    EDUCATION_PATHWAYS = "education_pathways"
    ACTION_PLAN = "action_plan"
    COMPLETION_REPORT = "completion_report"

class AssessmentType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE_RATING = "scale_rating"
    OPEN_ENDED = "open_ended"
    SCENARIO_BASED = "scenario_based"
    PERSONALITY_TEST = "personality_test"

class AssessmentQuestion(BaseModel):
    id: str
    question: str
    type: AssessmentType
    options: Optional[List[str]] = None
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    required: bool = True
    weight: float = 1.0

class AssessmentResponse(BaseModel):
    question_id: str
    answer: Any
    score: Optional[float] = None
    feedback: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StepAssessment(BaseModel):
    step_type: StepType
    questions: List[AssessmentQuestion]
    responses: List[AssessmentResponse] = []
    total_score: float = 0.0
    max_possible_score: float = 0.0
    completion_percentage: float = 0.0
    is_completed: bool = False

class CareerDomain(BaseModel):
    id: str
    title: str
    description: str
    match_score: float
    confidence_level: float
    reasoning: str
    required_skills: List[str]
    growth_potential: str
    salary_range: str

class LearningPathway(BaseModel):
    id: str
    title: str
    description: str
    duration: str
    cost_range: str
    institutions: List[str]
    prerequisites: List[str]
    career_outcomes: List[str]

class ActionItem(BaseModel):
    id: str
    title: str
    description: str
    priority: str  # high, medium, low
    timeline: str
    resources_needed: List[str]
    is_completed: bool = False

class ProgressMetrics(BaseModel):
    overall_score: float = 0.0
    steps_completed: int = 0
    total_steps: int = 10
    completion_percentage: float = 0.0
    time_spent_minutes: int = 0
    last_activity: Optional[datetime] = None

# Request Models
class StartSessionRequest(BaseModel):
    student_id: str = Field(..., example="student_123", description="Unique identifier for the student")
    language: Language = Field(..., example=Language.ENGLISH, description="Preferred language for the session")
    tier: Tier = Field(..., example=Tier.BASIC, description="Subscription tier level")
    student_name: Optional[str] = Field(None, example="John Doe", description="Student's full name")
    age: Optional[int] = Field(None, ge=13, le=100, example=18, description="Student's age")
    current_education_level: Optional[str] = Field(None, example="High School Senior", description="Current education level")

class StepRequest(BaseModel):
    session_id: str = Field(..., example="6ab0b5ac-9d4c-11ec-b909-0242ac120002", description="Session identifier")
    step_type: StepType = Field(..., description="Type of step being processed")
    input_text: Optional[str] = Field(None, example="I want to become a data scientist", description="User input for the step")
    assessment_responses: Optional[List[AssessmentResponse]] = Field(None, description="Assessment question responses")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the step")

class GetSessionRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier to retrieve")

class GetProgressRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier to get progress for")

class GenerateReportRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier to generate report for")
    format: str = Field(default="pdf", description="Report format (pdf, json, html)")

# Response Models
class StartSessionResponse(BaseModel):
    session_id: str
    message: str
    current_step: StepType
    total_steps: int
    estimated_duration: str
    welcome_message: str

class StepResponse(BaseModel):
    step_type: StepType
    step_number: int
    title: str
    description: str
    prompt: Optional[str] = None
    assessment: Optional[StepAssessment] = None
    career_domains: Optional[List[CareerDomain]] = None
    learning_pathways: Optional[List[LearningPathway]] = None
    action_items: Optional[List[ActionItem]] = None
    message: str
    next_step: Optional[StepType] = None
    is_completed: bool = False
    progress: ProgressMetrics

class SessionResponse(BaseModel):
    session_id: str
    student_id: str
    language: Language
    tier: Tier
    current_step: StepType
    step_number: int
    progress: ProgressMetrics
    assessments: List[StepAssessment]
    career_domains: List[CareerDomain]
    learning_pathways: List[LearningPathway]
    action_items: List[ActionItem]
    created_at: datetime
    last_updated: datetime

class ProgressResponse(BaseModel):
    session_id: str
    progress: ProgressMetrics
    step_details: List[Dict[str, Any]]
    recommendations: List[str]
    next_steps: List[str]

class ReportResponse(BaseModel):
    session_id: str
    report_url: Optional[str] = None
    report_data: Dict[str, Any]
    generated_at: datetime
    format: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None