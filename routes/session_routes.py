from fastapi import APIRouter, Depends, HTTPException, Query
from models.session_models import (
    StartSessionRequest, StartSessionResponse,
    StepRequest, StepResponse, GetSessionRequest, SessionResponse,
    GetProgressRequest, ProgressResponse, GenerateReportRequest, ReportResponse
)
from controllers.session_controller import (
    SessionController
)
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/start_session",
    response_model=StartSessionResponse,
    summary="Start a new CVP Lite session",
    description="Initializes a new Career Vision Program Lite session for a student with comprehensive assessment capabilities."
)
async def start_session(request: StartSessionRequest):
    """Start a new CVP Lite session"""
    try:
        return await SessionController.handle_start_session(
            student_id=request.student_id,
            language=request.language,
            tier=request.tier,
            student_name=request.student_name,
            age=request.age,
            current_education_level=request.current_education_level
        )
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/step",
    response_model=StepResponse,
    summary="Process a step in the CVP Lite program",
    description="Handles user input for a given step, processes assessments, and advances the session through the 10-step program."
)
async def process_step(request: StepRequest):
    """Process a step in the CVP Lite program"""
    try:
        return await SessionController.handle_step(request)
    except Exception as e:
        logger.error(f"Error processing step: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/session",
    response_model=SessionResponse,
    summary="Get complete session information",
    description="Retrieves comprehensive session information including all assessments, career recommendations, and progress data."
)
async def get_session(request: GetSessionRequest):
    """Get complete session information"""
    try:
        return await SessionController.handle_get_session(request)
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/progress",
    response_model=ProgressResponse,
    summary="Get session progress and recommendations",
    description="Retrieves detailed progress information, step-by-step completion status, and personalized recommendations."
)
async def get_progress(request: GetProgressRequest):
    """Get session progress and recommendations"""
    try:
        return await SessionController.handle_get_progress(request)
    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/report",
    response_model=ReportResponse,
    summary="Generate comprehensive session report",
    description="Generates a detailed report including career recommendations, learning pathways, action items, and AI-generated insights."
)
async def generate_report(request: GenerateReportRequest):
    """Generate comprehensive session report"""
    try:
        return await SessionController.handle_generate_report(request)
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/sessions",
    summary="List all sessions",
    description="Retrieves a list of all sessions with optional filtering and pagination."
)
async def list_sessions(
    student_id: Optional[str] = Query(None, description="Filter by student ID"),
    status: Optional[str] = Query(None, description="Filter by session status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of sessions to return"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip")
):
    """List all sessions with optional filtering"""
    try:
        # Build query
        query = {}
        if student_id:
            query["student_id"] = student_id
        if status:
            query["status"] = status
        
        # Get sessions from database
        from db.mongo_client import search_sessions
        sessions = await search_sessions(query, limit)
        
        # Apply pagination
        total_sessions = len(sessions)
        paginated_sessions = sessions[offset:offset + limit]
        
        return {
            "sessions": paginated_sessions,
            "total": total_sessions,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_sessions
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/sessions/{session_id}",
    summary="Get session by ID",
    description="Retrieves a specific session by its ID."
)
async def get_session_by_id(session_id: str):
    """Get session by ID"""
    try:
        from db.mongo_client import get_session
        session = await get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session by ID: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "/sessions/{session_id}",
    summary="Delete session",
    description="Deletes a session and all associated data."
)
async def delete_session(session_id: str):
    """Delete session"""
    try:
        from db.mongo_client import delete_session
        success = await delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/health",
    summary="Health check",
    description="Simple health check endpoint to verify the service is running."
)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "CVP Lite API"}

@router.get(
    "/stats",
    summary="Database statistics",
    description="Retrieves database statistics including session counts and assessment data."
)
async def get_stats():
    """Get database statistics"""
    try:
        from db.mongo_client import get_database_stats
        stats = await get_database_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/steps",
    summary="Get step information",
    description="Retrieves information about all available steps in the CVP Lite program."
)
async def get_steps():
    """Get information about all program steps"""
    try:
        from services.cvp_step_content import CVPStepContent
        from models.session_models import StepType
        
        steps = []
        for step_type in StepType:
            if step_type != StepType.COMPLETION_REPORT:  # Skip the completion report step
                content = CVPStepContent.get_step_content(step_type)
                steps.append({
                    "step_type": step_type.value,
                    "step_number": len(steps) + 1,
                    "title": content.get("title", ""),
                    "description": content.get("description", ""),
                    "prompt": content.get("prompt", "")
                })
        
        return {"steps": steps, "total_steps": len(steps)}
    except Exception as e:
        logger.error(f"Error getting steps: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/career-domains",
    summary="Get career domains",
    description="Retrieves all available career domains for career matching and recommendations."
)
async def get_career_domains():
    """Get all career domains"""
    try:
        from db.mongo_client import get_career_domains
        domains = await get_career_domains()
        return {"career_domains": domains, "total": len(domains)}
    except Exception as e:
        logger.error(f"Error getting career domains: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/learning-pathways",
    summary="Get learning pathways",
    description="Retrieves all available learning pathways for educational planning and career development."
)
async def get_learning_pathways():
    """Get all learning pathways"""
    try:
        from db.mongo_client import get_learning_pathways
        pathways = await get_learning_pathways()
        return {"learning_pathways": pathways, "total": len(pathways)}
    except Exception as e:
        logger.error(f"Error getting learning pathways: {e}")
        raise HTTPException(status_code=500, detail=str(e))