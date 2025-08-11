import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from models.session_models import (
    StepType, StepResponse, StartSessionResponse, SessionResponse,
    ProgressResponse, ReportResponse, StepAssessment, AssessmentResponse,
    CareerDomain, LearningPathway, ActionItem, ProgressMetrics,
    StepRequest, StartSessionRequest, GetSessionRequest, GetProgressRequest,
    GenerateReportRequest, Language, Tier
)
from services.cvp_step_content import CVPStepContent
from services.scoring_engine import ScoringEngine
from services.ai_mentor import AIMentor
from services.openai_client import generate_career_recommendations
from db.mongo_client import (
    save_session, get_session, save_assessment, get_assessments,
    get_career_domains, get_learning_pathways, save_career_domains,
    save_learning_pathways, get_session_progress, search_sessions
)
from app_config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionController:
    """Handles all session-related operations for the CVP Lite program"""
    
    @staticmethod
    async def handle_start_session(
        student_id: str, 
        language: Language, 
        tier: Tier,
        student_name: Optional[str] = None,
        age: Optional[int] = None,
        current_education_level: Optional[str] = None
    ) -> StartSessionResponse:
        """Start a new CVP Lite session"""
        try:
            session_id = str(uuid.uuid4())
            
            # Create session document
            session_doc = {
                "session_id": session_id,
                "student_id": student_id,
                "student_name": student_name,
                "age": age,
                "current_education_level": current_education_level,
                "language": language.value,
                "tier": tier.value,
                "current_step": StepType.PROFILE_SETUP.value,
                "step_number": 1,
                "created_at": datetime.utcnow(),
                "last_updated": datetime.utcnow(),
                "status": "active"
            }
            
            # Save session to database
            await save_session(session_doc)
            
            # Initialize career domains and learning pathways if not exists
            await SessionController._initialize_career_data()
            
            # Generate welcome message
            welcome_message = await AIMentor.generate_step_prompt(
                StepType.PROFILE_SETUP,
                language,
                None,
                None
            )
            
            logger.info(f"Started new session {session_id} for student {student_id}")
            
            return StartSessionResponse(
                session_id=session_id,
                message=f"Session started for student {student_id}",
                current_step=StepType.PROFILE_SETUP,
                total_steps=settings.MAX_STEPS,
                estimated_duration="45-60 minutes",
                welcome_message=welcome_message
            )
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            raise Exception(f"Failed to start session: {str(e)}")
    
    @staticmethod
    async def handle_step(request: StepRequest) -> StepResponse:
        """Process a step in the CVP Lite program"""
        try:
            # Get session
            session = await get_session(request.session_id)
            if not session:
                raise Exception("Session not found")
            
            step_type = request.step_type
            step_number = SessionController._get_step_number(step_type)
            
            # Get step content
            step_content = CVPStepContent.get_step_content(step_type, session.get("language", "en"))
            
            # Process assessment responses if provided
            assessment = None
            if request.assessment_responses:
                assessment = await SessionController._process_assessment(
                    step_type, request.assessment_responses, session
                )
            
            # Get career domains and learning pathways for later steps
            career_domains = []
            learning_pathways = []
            action_items = []
            
            if step_number >= 7:  # Career summary and beyond
                career_domains = await SessionController._get_career_recommendations(session)
                learning_pathways = await SessionController._get_learning_recommendations(session)
            
            if step_number >= 9:  # Action plan step
                action_items = await SessionController._generate_action_items(session)
            
            # Calculate progress
            progress = await SessionController._calculate_progress(session)
            
            # Determine next step
            next_step = SessionController._get_next_step(step_type, assessment)
            
            # Update session
            await SessionController._update_session_progress(session, step_type, step_number, assessment)
            
            # Generate AI mentor message
            ai_message = await SessionController._generate_ai_message(step_type, assessment, progress)
            
            logger.info(f"Processed step {step_number} for session {request.session_id}")
            
            return StepResponse(
                step_type=step_type,
                step_number=step_number,
                title=step_content.get("title", f"Step {step_number}"),
                description=step_content.get("description", ""),
                prompt=step_content.get("prompt", ""),
                assessment=assessment,
                career_domains=career_domains,
                learning_pathways=learning_pathways,
                action_items=action_items,
                message=ai_message,
                next_step=next_step,
                is_completed=assessment.is_completed if assessment else False,
                progress=progress
            )
            
        except Exception as e:
            logger.error(f"Error processing step: {e}")
            raise Exception(f"Failed to process step: {str(e)}")
    
    @staticmethod
    async def handle_get_session(request: GetSessionRequest) -> SessionResponse:
        """Get complete session information"""
        try:
            session = await get_session(request.session_id)
            if not session:
                raise Exception("Session not found")
            
            # Get all assessments
            assessments = await get_assessments(request.session_id)
            
            # Get career domains and learning pathways
            career_domains = await get_career_domains()
            learning_pathways = await get_learning_pathways()
            
            # Calculate progress
            progress = await SessionController._calculate_progress(session)
            
            # Generate action items
            action_items = await SessionController._generate_action_items(session)
            
            return SessionResponse(
                session_id=session["session_id"],
                student_id=session["student_id"],
                language=Language(session["language"]),
                tier=Tier(session["tier"]),
                current_step=StepType(session["current_step"]),
                step_number=session.get("step_number", 1),
                progress=progress,
                assessments=[],  # Convert to proper models if needed
                career_domains=[],  # Convert to proper models if needed
                learning_pathways=[],  # Convert to proper models if needed
                action_items=action_items,
                created_at=session["created_at"],
                last_updated=session["last_updated"]
            )
            
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            raise Exception(f"Failed to get session: {str(e)}")
    
    @staticmethod
    async def handle_get_progress(request: GetProgressRequest) -> ProgressResponse:
        """Get session progress and recommendations"""
        try:
            # Get progress from database
            progress_data = await get_session_progress(request.session_id)
            if not progress_data:
                raise Exception("Session not found")
            
            # Get session details
            session = await get_session(request.session_id)
            assessments = await get_assessments(request.session_id)
            
            # Calculate detailed progress
            progress = await SessionController._calculate_progress(session)
            
            # Get step details
            step_details = await SessionController._get_step_details(session, assessments)
            
            # Generate recommendations
            recommendations = await SessionController._generate_recommendations(session, assessments)
            
            # Get next steps
            next_steps = await SessionController._get_next_steps(session, assessments)
            
            return ProgressResponse(
                session_id=request.session_id,
                progress=progress,
                step_details=step_details,
                recommendations=recommendations,
                next_steps=next_steps
            )
            
        except Exception as e:
            logger.error(f"Error getting progress: {e}")
            raise Exception(f"Failed to get progress: {str(e)}")
    
    @staticmethod
    async def handle_generate_report(request: GenerateReportRequest) -> ReportResponse:
        """Generate comprehensive report for the session"""
        try:
            # Get session and assessments
            session = await get_session(request.session_id)
            if not session:
                raise Exception("Session not found")
            
            assessments = await get_assessments(request.session_id)
            career_domains = await get_career_domains()
            learning_pathways = await get_learning_pathways()
            
            # Generate report data
            report_data = await SessionController._generate_report_data(
                session, assessments, career_domains, learning_pathways
            )
            
            # For now, return JSON format (PDF generation would be implemented separately)
            report_url = None  # Would be generated for PDF format
            
            return ReportResponse(
                session_id=request.session_id,
                report_url=report_url,
                report_data=report_data,
                generated_at=datetime.utcnow(),
                format=request.format
            )
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise Exception(f"Failed to generate report: {str(e)}")
    
    # Helper methods
    
    @staticmethod
    def _get_step_number(step_type: StepType) -> int:
        """Get the numerical order of a step"""
        step_order = {
            StepType.PROFILE_SETUP: 1,
            StepType.INTERESTS_STRENGTHS: 2,
            StepType.VALUES_PREFERENCES: 3,
            StepType.LEARNING_PERSONALITY: 4,
            StepType.PASSION_CAREER_FIT: 5,
            StepType.COGNITIVE_THINKING: 6,
            StepType.EMOTIONAL_ETHICAL: 7,
            StepType.CAREER_SUMMARY: 8,
            StepType.EDUCATION_PATHWAYS: 9,
            StepType.ACTION_PLAN: 10
        }
        return step_order.get(step_type, 1)
    
    @staticmethod
    async def _process_assessment(
        step_type: StepType,
        responses: List[AssessmentResponse],
        session: Dict[str, Any]
    ) -> StepAssessment:
        """Process assessment responses and calculate scores"""
        # Get step content for questions
        step_content = CVPStepContent.get_step_content(step_type, session.get("language", "en"))
        questions = step_content.get("assessment", {}).get("questions", [])
        
        # Create assessment
        assessment = StepAssessment(
            step_type=step_type,
            questions=questions,
            responses=responses
        )
        
        # Calculate scores
        total_score, max_score, completion_percentage = ScoringEngine.calculate_assessment_score(assessment)
        assessment.total_score = total_score
        assessment.max_possible_score = max_score
        assessment.completion_percentage = completion_percentage
        assessment.is_completed = completion_percentage >= 80  # 80% completion threshold
        
        # Save assessment to database
        assessment_doc = {
            "session_id": session["session_id"],
            "step_type": step_type.value,
            "step_number": SessionController._get_step_number(step_type),
            "questions": [q.dict() for q in questions],
            "responses": [r.dict() for r in responses],
            "total_score": total_score,
            "max_possible_score": max_score,
            "completion_percentage": completion_percentage,
            "is_completed": assessment.is_completed,
            "created_at": datetime.utcnow()
        }
        
        await save_assessment(assessment_doc)
        
        return assessment
    
    @staticmethod
    async def _get_career_recommendations(session: Dict[str, Any]) -> List[CareerDomain]:
        """Get career recommendations based on session data"""
        try:
            # Get assessments
            assessments = await get_assessments(session["session_id"])
            
            # Get career domains
            career_domains = await get_career_domains()
            
            # Calculate matches
            if assessments and career_domains:
                # Convert to proper models for scoring
                step_assessments = []
                for assessment in assessments:
                    # Convert database assessment to StepAssessment model
                    # This is simplified - in production you'd have proper conversion
                    pass
                
                # For now, return basic career domains
                return career_domains[:5]  # Top 5
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting career recommendations: {e}")
            return []
    
    @staticmethod
    async def _get_learning_recommendations(session: Dict[str, Any]) -> List[LearningPathway]:
        """Get learning pathway recommendations"""
        try:
            learning_pathways = await get_learning_pathways()
            return learning_pathways[:3]  # Top 3 pathways
        except Exception as e:
            logger.error(f"Error getting learning recommendations: {e}")
            return []
    
    @staticmethod
    async def _generate_action_items(session: Dict[str, Any]) -> List[ActionItem]:
        """Generate personalized action items"""
        try:
            # Get assessments to understand student's situation
            assessments = await get_assessments(session["session_id"])
            
            # Generate basic action items based on step completion
            action_items = []
            
            if len(assessments) < 5:
                action_items.append(ActionItem(
                    id="complete_assessments",
                    title="Complete Core Assessments",
                    description="Finish the remaining assessment steps to get better career insights",
                    priority="high",
                    timeline="1-2 weeks",
                    resources_needed=["Time for reflection", "Honest self-assessment"]
                ))
            
            action_items.append(ActionItem(
                id="research_careers",
                title="Research Career Options",
                description="Explore the career paths that interest you most",
                priority="medium",
                timeline="Ongoing",
                resources_needed=["Internet access", "Career websites", "Professional networks"]
            ))
            
            action_items.append(ActionItem(
                id="skill_development",
                title="Develop Key Skills",
                description="Focus on building skills relevant to your target career",
                priority="medium",
                timeline="3-6 months",
                resources_needed=["Online courses", "Practice opportunities", "Mentorship"]
            ))
            
            return action_items
            
        except Exception as e:
            logger.error(f"Error generating action items: {e}")
            return []
    
    @staticmethod
    async def _calculate_progress(session: Dict[str, Any]) -> ProgressMetrics:
        """Calculate overall progress for the session"""
        try:
            # Get assessments count
            assessments = await get_assessments(session["session_id"])
            completed_steps = sum(1 for a in assessments if a.get("is_completed", False))
            
            # Calculate completion percentage
            completion_percentage = (completed_steps / settings.MAX_STEPS) * 100
            
            # Estimate time spent (simplified calculation)
            time_spent_minutes = len(assessments) * 5  # 5 minutes per assessment
            
            return ProgressMetrics(
                overall_score=completion_percentage,  # Simplified scoring
                steps_completed=completed_steps,
                total_steps=settings.MAX_STEPS,
                completion_percentage=completion_percentage,
                time_spent_minutes=time_spent_minutes,
                last_activity=session.get("last_updated")
            )
            
        except Exception as e:
            logger.error(f"Error calculating progress: {e}")
            return ProgressMetrics()
    
    @staticmethod
    def _get_next_step(current_step: StepType, assessment: Optional[StepAssessment]) -> Optional[StepType]:
        """Determine the next step based on current step and completion"""
        if not assessment or not assessment.is_completed:
            return current_step
        
        # Define step progression
        step_progression = {
            StepType.PROFILE_SETUP: StepType.INTERESTS_STRENGTHS,
            StepType.INTERESTS_STRENGTHS: StepType.VALUES_PREFERENCES,
            StepType.VALUES_PREFERENCES: StepType.LEARNING_PERSONALITY,
            StepType.LEARNING_PERSONALITY: StepType.PASSION_CAREER_FIT,
            StepType.PASSION_CAREER_FIT: StepType.COGNITIVE_THINKING,
            StepType.COGNITIVE_THINKING: StepType.EMOTIONAL_ETHICAL,
            StepType.EMOTIONAL_ETHICAL: StepType.CAREER_SUMMARY,
            StepType.CAREER_SUMMARY: StepType.EDUCATION_PATHWAYS,
            StepType.EDUCATION_PATHWAYS: StepType.ACTION_PLAN,
            StepType.ACTION_PLAN: None  # Final step
        }
        
        return step_progression.get(current_step)
    
    @staticmethod
    async def _update_session_progress(
        session: Dict[str, Any], 
        step_type: StepType, 
        step_number: int, 
        assessment: Optional[StepAssessment]
    ):
        """Update session with new progress information"""
        try:
            update_data = {
                "current_step": step_type.value,
                "step_number": step_number,
                "last_updated": datetime.utcnow()
            }
            
            if assessment and assessment.is_completed:
                update_data["last_completed_step"] = step_type.value
                update_data["last_completed_step_number"] = step_number
            
            await save_session({
                **session,
                **update_data
            })
            
        except Exception as e:
            logger.error(f"Error updating session progress: {e}")
    
    @staticmethod
    async def _generate_ai_message(
        step_type: StepType, 
        assessment: Optional[StepAssessment], 
        progress: ProgressMetrics
    ) -> str:
        """Generate AI mentor message for the step"""
        try:
            if assessment and assessment.is_completed:
                return await AIMentor.generate_step_prompt(
                    step_type,
                    Language.ENGLISH,  # Default language for now
                    assessment.responses if assessment else None,
                    progress
                )
            else:
                return "Please complete the assessment questions to continue with your career exploration journey."
                
        except Exception as e:
            logger.error(f"Error generating AI message: {e}")
            return "Let's continue exploring your career path together!"
    
    @staticmethod
    async def _initialize_career_data():
        """Initialize career domains and learning pathways in database"""
        try:
            # Check if data already exists
            existing_domains = await get_career_domains()
            existing_pathways = await get_learning_pathways()
            
            if not existing_domains:
                # Get career domains from content service
                career_domains = CVPStepContent.get_career_domains()
                domain_docs = []
                for domain in career_domains:
                    domain_docs.append({
                        "domain_id": domain.id,
                        "title": domain.title,
                        "description": domain.description,
                        "required_skills": domain.required_skills,
                        "growth_potential": domain.growth_potential,
                        "salary_range": domain.salary_range,
                        "created_at": datetime.utcnow()
                    })
                
                if domain_docs:
                    await save_career_domains(domain_docs)
            
            if not existing_pathways:
                # Get learning pathways from content service
                learning_pathways = CVPStepContent.get_learning_pathways()
                pathway_docs = []
                for pathway in learning_pathways:
                    pathway_docs.append({
                        "pathway_id": pathway.id,
                        "title": pathway.title,
                        "description": pathway.description,
                        "duration": pathway.duration,
                        "cost_range": pathway.cost_range,
                        "institutions": pathway.institutions,
                        "prerequisites": pathway.prerequisites,
                        "career_outcomes": pathway.career_outcomes,
                        "created_at": datetime.utcnow()
                    })
                
                if pathway_docs:
                    await save_learning_pathways(pathway_docs)
                    
        except Exception as e:
            logger.error(f"Error initializing career data: {e}")
    
    @staticmethod
    async def _get_step_details(session: Dict[str, Any], assessments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get detailed information about each step"""
        step_details = []
        
        for i in range(1, settings.MAX_STEPS + 1):
            step_info = {
                "step_number": i,
                "status": "not_started",
                "completion_percentage": 0,
                "score": 0
            }
            
            # Find assessment for this step
            for assessment in assessments:
                if assessment.get("step_number") == i:
                    step_info["status"] = "completed" if assessment.get("is_completed") else "in_progress"
                    step_info["completion_percentage"] = assessment.get("completion_percentage", 0)
                    step_info["score"] = assessment.get("total_score", 0)
                    break
            
            step_details.append(step_info)
        
        return step_details
    
    @staticmethod
    async def _generate_recommendations(session: Dict[str, Any], assessments: List[Dict[str, Any]]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Basic recommendations based on progress
        if len(assessments) < 3:
            recommendations.append("Complete more assessment steps to get personalized career guidance")
        elif len(assessments) < 7:
            recommendations.append("You're building a solid foundation. Continue with the remaining assessments")
        else:
            recommendations.append("Great progress! Focus on implementing your action plan")
        
        # Add tier-specific recommendations
        if session.get("tier") == "premium":
            recommendations.append("As a premium user, you have access to advanced career insights and personalized coaching")
        elif session.get("tier") == "enterprise":
            recommendations.append("Your enterprise access includes comprehensive career planning tools and expert guidance")
        
        return recommendations
    
    @staticmethod
    async def _get_next_steps(session: Dict[str, Any], assessments: List[Dict[str, Any]]) -> List[str]:
        """Get actionable next steps"""
        next_steps = []
        
        # Determine current progress and suggest next actions
        completed_steps = len([a for a in assessments if a.get("is_completed")])
        
        if completed_steps < 5:
            next_steps.append("Complete the core assessment steps (1-5) to understand your career preferences")
        elif completed_steps < 8:
            next_steps.append("Finish the remaining assessments to get your career summary")
        elif completed_steps < 10:
            next_steps.append("Complete the final steps to create your action plan")
        else:
            next_steps.append("Implement your action plan and start your career journey")
            next_steps.append("Schedule follow-up sessions to track your progress")
        
        return next_steps
    
    @staticmethod
    async def _generate_report_data(
        session: Dict[str, Any], 
        assessments: List[Dict[str, Any]], 
        career_domains: List[Dict[str, Any]], 
        learning_pathways: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive report data"""
        try:
            # Calculate overall progress
            progress = await SessionController._calculate_progress(session)
            
            # Get career recommendations
            career_recommendations = await SessionController._get_career_recommendations(session)
            
            # Generate AI insights
            ai_insights = await AIMentor.generate_career_insights(
                [],  # Convert assessments to proper models if needed
                career_recommendations
            )
            
            report_data = {
                "session_info": {
                    "session_id": session["session_id"],
                    "student_id": session["student_id"],
                    "created_at": session["created_at"],
                    "completed_at": datetime.utcnow()
                },
                "progress_summary": {
                    "overall_score": progress.overall_score,
                    "steps_completed": progress.steps_completed,
                    "total_steps": progress.total_steps,
                    "completion_percentage": progress.completion_percentage,
                    "time_spent_minutes": progress.time_spent_minutes
                },
                "career_recommendations": career_recommendations[:5],  # Top 5
                "learning_pathways": learning_pathways[:3],  # Top 3
                "ai_insights": ai_insights,
                "action_items": await SessionController._generate_action_items(session),
                "generated_at": datetime.utcnow()
            }
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating report data: {e}")
            return {"error": "Failed to generate report data"}