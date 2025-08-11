from fastapi import APIRouter, Depends, HTTPException
from models.session_models import (
    StartSessionRequest, StartSessionResponse,
    StepRequest, StepResponse
)
from controllers.session_controller import handle_start_session, handle_step

router = APIRouter()

@router.post(
    "/start_session",
    response_model=StartSessionResponse,
    summary="Start a new session",
    description="Initializes a new CVP Lite session for a student."
)
async def start_session(request: StartSessionRequest):
    return await handle_start_session(
        request.student_id, request.language, request.tier
    )

@router.post(
    "/step",
    response_model=StepResponse,
    summary="Process a step in the session",
    description="Handles user input for a given step and advances the session."
)
async def step(request: StepRequest):
    return await handle_step(
        request.session_id, request.input_text
    )