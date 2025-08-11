from typing import Dict, List, Any, Optional
from models.session_models import (
    StepType, AssessmentResponse, StepAssessment, 
    CareerDomain, ProgressMetrics, Language
)
from services.openai_client import generate_completion
from services.scoring_engine import ScoringEngine
import json

class AIMentor:
    """AI-powered mentor system for CVP Lite program"""
    
    # System prompts for different contexts
    SYSTEM_PROMPTS = {
        "general": """You are an AI career mentor for the CVP Lite program. Your role is to:
1. Provide encouraging and supportive guidance
2. Help students reflect on their responses
3. Offer insights based on assessment data
4. Guide them through career exploration
5. Maintain a conversational, mentor-like tone

Always be positive, encouraging, and help students think deeper about their career goals.""",
        
        "assessment_feedback": """You are providing feedback on assessment responses. Focus on:
1. Acknowledging their honest responses
2. Highlighting positive insights
3. Encouraging deeper reflection
4. Connecting responses to career possibilities
5. Maintaining an encouraging tone""",
        
        "career_guidance": """You are providing career guidance based on assessment results. Focus on:
1. Connecting their interests and strengths to career paths
2. Suggesting exploration opportunities
3. Addressing concerns constructively
4. Providing actionable next steps
5. Being realistic but optimistic about possibilities""",
        
        "step_transition": """You are helping students transition between program steps. Focus on:
1. Summarizing what they've accomplished
2. Explaining what's coming next
3. Building excitement for the next phase
4. Addressing any concerns about moving forward
5. Maintaining momentum and engagement"""
    }
    
    @staticmethod
    async def generate_step_prompt(
        step_type: StepType,
        language: Language = Language.ENGLISH,
        previous_responses: Optional[List[AssessmentResponse]] = None,
        progress: Optional[ProgressMetrics] = None
    ) -> str:
        """Generate a personalized prompt for the current step"""
        
        base_prompts = {
            StepType.PROFILE_SETUP: "Welcome to your career journey! Let's start by understanding your background and aspirations.",
            StepType.INTERESTS_STRENGTHS: "Now let's explore what truly excites you and where your natural talents lie.",
            StepType.VALUES_PREFERENCES: "Understanding your values helps us find career paths that align with what matters most to you.",
            StepType.LEARNING_PERSONALITY: "Let's discover how you learn best and understand your unique personality traits.",
            StepType.PASSION_CAREER_FIT: "Now we'll connect your passions with potential career opportunities.",
            StepType.COGNITIVE_THINKING: "Let's explore how you approach problems and make decisions.",
            StepType.EMOTIONAL_ETHICAL: "Understanding your emotional intelligence and ethical decision-making is crucial for career success.",
            StepType.CAREER_SUMMARY: "Based on our journey together, let's summarize your career direction.",
            StepType.EDUCATION_PATHWAYS: "Now let's explore the educational paths that can lead to your career goals.",
            StepType.ACTION_PLAN: "Finally, let's create a concrete action plan to move forward."
        }
        
        base_prompt = base_prompts.get(step_type, "Let's continue exploring your career path.")
        
        # Personalize based on previous responses
        if previous_responses:
            personalization = AIMentor._generate_personalization(previous_responses, step_type)
            if personalization:
                base_prompt += f" {personalization}"
        
        # Add progress motivation
        if progress and progress.completion_percentage > 0:
            if progress.completion_percentage < 30:
                base_prompt += " You're just getting started - every step brings us closer to your career clarity!"
            elif progress.completion_percentage < 70:
                base_prompt += " You're making great progress! We're building a solid foundation for your career decisions."
            else:
                base_prompt += " You're almost there! Your insights are coming together beautifully."
        
        return base_prompt
    
    @staticmethod
    async def generate_assessment_feedback(
        question_id: str,
        response: AssessmentResponse,
        step_type: StepType,
        language: Language = Language.ENGLISH
    ) -> str:
        """Generate personalized feedback for assessment responses"""
        
        # Basic feedback templates
        feedback_templates = {
            "profile": {
                "positive": "That's a great starting point! Your background in {response} gives us valuable insights.",
                "encouraging": "Thank you for sharing that. Every piece of information helps us understand your unique path better."
            },
            "interests": {
                "positive": "Your interest in {response} shows real passion! This could open up exciting career possibilities.",
                "encouraging": "That's fascinating! Interests like yours often translate into fulfilling career paths."
            },
            "strengths": {
                "positive": "Recognizing your strength in {response} is powerful! These are the building blocks of your career success.",
                "encouraging": "That's a wonderful insight about yourself. Your strengths will guide us to the right career choices."
            },
            "values": {
                "positive": "Your value of {response} is fundamental to finding career satisfaction. This will guide our exploration.",
                "encouraging": "That's a deeply important value. Careers that align with your values lead to the most fulfillment."
            }
        }
        
        # Determine feedback type based on question
        if "profile" in question_id:
            feedback_type = "profile"
        elif "interests" in question_id:
            feedback_type = "interests"
        elif "strengths" in question_id:
            feedback_type = "strengths"
        elif "values" in question_id:
            feedback_type = "values"
        else:
            feedback_type = "general"
        
        # Generate appropriate feedback
        if feedback_type in feedback_templates:
            if response.answer and len(str(response.answer).strip()) > 10:
                return feedback_templates[feedback_type]["positive"].format(response=response.answer)
            else:
                return feedback_templates[feedback_type]["encouraging"]
        
        # Default feedback
        return "Thank you for sharing that insight. Every response helps us understand your career path better."
    
    @staticmethod
    async def generate_career_insights(
        assessments: List[StepAssessment],
        career_domains: List[CareerDomain],
        language: Language = Language.ENGLISH
    ) -> Dict[str, Any]:
        """Generate AI-powered career insights and recommendations"""
        
        insights = {
            "summary": "",
            "key_strengths": [],
            "growth_areas": [],
            "career_highlights": [],
            "next_steps": []
        }
        
        # Extract key insights from assessments
        if assessments:
            # Identify strengths
            strengths = AIMentor._extract_strengths(assessments)
            insights["key_strengths"] = strengths[:3]  # Top 3 strengths
            
            # Identify growth areas
            growth_areas = AIMentor._identify_growth_areas(assessments)
            insights["growth_areas"] = growth_areas[:2]  # Top 2 growth areas
            
            # Generate career highlights
            if career_domains:
                insights["career_highlights"] = AIMentor._generate_career_highlights(career_domains)
            
            # Generate summary
            insights["summary"] = AIMentor._generate_insights_summary(assessments, career_domains)
            
            # Generate next steps
            insights["next_steps"] = AIMentor._generate_next_steps(assessments, career_domains)
        
        return insights
    
    @staticmethod
    async def generate_conversation_response(
        user_input: str,
        step_type: StepType,
        context: Dict[str, Any],
        language: Language = Language.ENGLISH
    ) -> str:
        """Generate conversational responses for user interactions"""
        
        # Create context-aware prompt
        prompt = f"""
        Context: You are an AI career mentor helping a student through the {step_type.value} step.
        Current context: {json.dumps(context, default=str)}
        User input: {user_input}
        
        Provide a helpful, encouraging response that:
        1. Addresses their input directly
        2. Provides relevant guidance for their current step
        3. Maintains a supportive mentor tone
        4. Encourages deeper reflection
        5. Keeps them engaged in the process
        
        Response:"""
        
        try:
            response = await generate_completion(prompt)
            return response.strip()
        except Exception as e:
            # Fallback response if AI generation fails
            return AIMentor._generate_fallback_response(user_input, step_type)
    
    @staticmethod
    def _generate_personalization(
        responses: List[AssessmentResponse], 
        current_step: StepType
    ) -> str:
        """Generate personalization based on previous responses"""
        
        if not responses:
            return ""
        
        # Extract key themes from responses
        themes = []
        for response in responses:
            if response.answer:
                answer = str(response.answer).lower()
                if "technology" in answer or "tech" in answer:
                    themes.append("technology")
                elif "helping" in answer or "people" in answer:
                    themes.append("helping others")
                elif "creative" in answer or "art" in answer:
                    themes.append("creativity")
                elif "science" in answer or "research" in answer:
                    themes.append("scientific inquiry")
                elif "business" in answer or "leadership" in answer:
                    themes.append("business leadership")
        
        if themes:
            unique_themes = list(set(themes))[:2]  # Limit to 2 themes
            if len(unique_themes) == 1:
                return f"I noticed your interest in {unique_themes[0]}. This could be very relevant to what we'll explore next."
            else:
                return f"I see you're drawn to {unique_themes[0]} and {unique_themes[1]}. These interests will help guide our exploration."
        
        return ""
    
    @staticmethod
    def _extract_strengths(assessments: List[StepAssessment]) -> List[str]:
        """Extract key strengths from assessments"""
        strengths = []
        
        for assessment in assessments:
            if assessment.step_type == StepType.INTERESTS_STRENGTHS:
                for response in assessment.responses:
                    if "strengths" in response.question_id and response.answer:
                        strengths.append(str(response.answer))
        
        return strengths
    
    @staticmethod
    def _identify_growth_areas(assessments: List[StepAssessment]) -> List[str]:
        """Identify areas for growth based on assessments"""
        growth_areas = []
        
        # Add common growth areas based on typical student needs
        growth_areas.extend([
            "Career research and exploration",
            "Professional networking",
            "Skill development planning",
            "Industry knowledge building"
        ])
        
        return growth_areas
    
    @staticmethod
    def _generate_career_highlights(career_domains: List[CareerDomain]) -> List[str]:
        """Generate career highlights from top matches"""
        highlights = []
        
        for domain in career_domains[:3]:  # Top 3 matches
            if domain.match_score > 70:
                highlights.append(f"Strong match with {domain.title} ({domain.match_score:.0f}% match)")
            elif domain.match_score > 50:
                highlights.append(f"Good potential in {domain.title} ({domain.match_score:.0f}% match)")
        
        return highlights
    
    @staticmethod
    def _generate_insights_summary(
        assessments: List[StepAssessment], 
        career_domains: List[CareerDomain]
    ) -> str:
        """Generate a summary of insights"""
        
        completed_steps = sum(1 for a in assessments if a.is_completed)
        total_steps = len(assessments)
        
        if completed_steps == 0:
            return "You're just beginning your career exploration journey. Each step will reveal more about your potential career paths."
        elif completed_steps < total_steps // 2:
            return f"You've completed {completed_steps} out of {total_steps} steps. You're building a solid foundation for understanding your career preferences."
        else:
            return f"You've made excellent progress, completing {completed_steps} out of {total_steps} steps. Your career direction is becoming clearer!"
    
    @staticmethod
    def _generate_next_steps(
        assessments: List[StepAssessment], 
        career_domains: List[CareerDomain]
    ) -> List[str]:
        """Generate actionable next steps"""
        next_steps = []
        
        # Add step-specific next steps
        completed_steps = [a.step_type for a in assessments if a.is_completed]
        
        if StepType.PROFILE_SETUP not in completed_steps:
            next_steps.append("Complete your profile setup to begin the assessment process")
        elif StepType.INTERESTS_STRENGTHS not in completed_steps:
            next_steps.append("Explore your interests and strengths to discover career possibilities")
        elif StepType.CAREER_SUMMARY not in completed_steps:
            next_steps.append("Review your career summary to solidify your direction")
        elif StepType.ACTION_PLAN not in completed_steps:
            next_steps.append("Create your action plan to move forward with your career goals")
        else:
            next_steps.append("Research specific companies and roles in your chosen field")
            next_steps.append("Connect with professionals in your target industry")
            next_steps.append("Begin implementing your action plan steps")
        
        return next_steps
    
    @staticmethod
    def _generate_fallback_response(user_input: str, step_type: StepType) -> str:
        """Generate a fallback response if AI generation fails"""
        
        fallback_responses = {
            StepType.PROFILE_SETUP: "That's a great question! Let's focus on understanding your background first. Could you tell me more about your current situation?",
            StepType.INTERESTS_STRENGTHS: "I appreciate your input! Let's explore what truly interests you. What activities make you lose track of time?",
            StepType.VALUES_PREFERENCES: "Thank you for sharing that! Values are so important in career decisions. What matters most to you in a job?",
            StepType.LEARNING_PERSONALITY: "That's interesting! Understanding how you learn best will help us find the right career path. How do you prefer to pick up new skills?",
            StepType.PASSION_CAREER_FIT: "Your passion is valuable! Let's think about how your interests could translate into a career. What problems would you like to solve?",
            StepType.COGNITIVE_THINKING: "Great question! Problem-solving approaches vary by person. How do you typically tackle complex challenges?",
            StepType.EMOTIONAL_ETHICAL: "That's an important consideration! Emotional intelligence is crucial in any career. How do you handle difficult situations?",
            StepType.CAREER_SUMMARY: "Let's reflect on what we've discovered together. What career path feels most aligned with your assessments?",
            StepType.EDUCATION_PATHWAYS: "Education is a key part of career planning. What type of learning environment appeals to you most?",
            StepType.ACTION_PLAN: "Action planning is exciting! Let's think about your first concrete step. What's one thing you could do this week to move forward?"
        }
        
        return fallback_responses.get(step_type, "Thank you for sharing that! Let's continue exploring your career path together.") 