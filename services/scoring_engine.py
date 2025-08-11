from typing import List, Dict, Any, Tuple
from models.session_models import (
    StepAssessment, AssessmentResponse, AssessmentQuestion,
    CareerDomain, ProgressMetrics, StepType
)
import math

class ScoringEngine:
    """Implements the progressive scoring logic system for CVP Lite"""
    
    # Scoring weights for different assessment types
    ASSESSMENT_WEIGHTS = {
        "multiple_choice": 1.0,
        "scale_rating": 1.0,
        "open_ended": 1.5,
        "scenario_based": 2.0,
        "personality_test": 1.2
    }
    
    # Step importance weights (higher = more important for overall score)
    STEP_WEIGHTS = {
        StepType.PROFILE_SETUP: 0.8,
        StepType.INTERESTS_STRENGTHS: 1.2,
        StepType.VALUES_PREFERENCES: 1.0,
        StepType.LEARNING_PERSONALITY: 1.1,
        StepType.PASSION_CAREER_FIT: 1.3,
        StepType.COGNITIVE_THINKING: 1.4,
        StepType.EMOTIONAL_ETHICAL: 1.1,
        StepType.CAREER_SUMMARY: 1.5,
        StepType.EDUCATION_PATHWAYS: 1.0,
        StepType.ACTION_PLAN: 1.2
    }
    
    # Career domain matching criteria weights
    CAREER_MATCH_WEIGHTS = {
        "interests": 0.25,
        "skills": 0.30,
        "values": 0.20,
        "personality": 0.15,
        "goals": 0.10
    }
    
    @staticmethod
    def calculate_assessment_score(assessment: StepAssessment) -> Tuple[float, float, float]:
        """
        Calculate the score for a specific assessment
        Returns: (total_score, max_possible_score, completion_percentage)
        """
        if not assessment.responses:
            return 0.0, 0.0, 0.0
        
        total_score = 0.0
        max_possible_score = 0.0
        answered_questions = 0
        
        for response in assessment.responses:
            question = next((q for q in assessment.questions if q.id == response.question_id), None)
            if question:
                score = ScoringEngine._score_response(question, response)
                if score is not None:
                    total_score += score * question.weight
                    max_possible_score += question.weight
                    answered_questions += 1
        
        # Calculate completion percentage
        completion_percentage = (answered_questions / len(assessment.questions)) * 100
        
        # Normalize score to 0-100 range
        if max_possible_score > 0:
            normalized_score = (total_score / max_possible_score) * 100
        else:
            normalized_score = 0.0
        
        return normalized_score, max_possible_score, completion_percentage
    
    @staticmethod
    def _score_response(question: AssessmentQuestion, response: AssessmentResponse) -> float:
        """Score an individual response based on question type"""
        if question.type.value == "multiple_choice":
            return ScoringEngine._score_multiple_choice(question, response)
        elif question.type.value == "scale_rating":
            return ScoringEngine._score_scale_rating(question, response)
        elif question.type.value == "open_ended":
            return ScoringEngine._score_open_ended(question, response)
        elif question.type.value == "scenario_based":
            return ScoringEngine._score_scenario_based(question, response)
        elif question.type.value == "personality_test":
            return ScoringEngine._score_personality_test(question, response)
        else:
            return 0.0
    
    @staticmethod
    def _score_multiple_choice(question: AssessmentQuestion, response: AssessmentResponse) -> float:
        """Score multiple choice questions"""
        # For multiple choice, we assume all options are valid
        # The score is based on whether they provided a meaningful answer
        if response.answer and response.answer in question.options:
            return 1.0
        return 0.0
    
    @staticmethod
    def _score_scale_rating(question: AssessmentQuestion, response: AssessmentResponse) -> float:
        """Score scale rating questions"""
        try:
            answer = float(response.answer)
            if question.scale_min <= answer <= question.scale_max:
                # Normalize to 0-1 scale
                normalized = (answer - question.scale_min) / (question.scale_max - question.scale_min)
                return normalized
        except (ValueError, TypeError):
            pass
        return 0.0
    
    @staticmethod
    def _score_open_ended(question: AssessmentQuestion, response: AssessmentResponse) -> float:
        """Score open-ended questions using AI analysis or length/content heuristics"""
        if not response.answer:
            return 0.0
        
        answer = str(response.answer).strip()
        
        # Basic scoring based on answer length and content
        if len(answer) < 10:
            return 0.3
        elif len(answer) < 25:
            return 0.6
        elif len(answer) < 50:
            return 0.8
        else:
            return 1.0
    
    @staticmethod
    def _score_scenario_based(question: AssessmentQuestion, response: AssessmentResponse) -> float:
        """Score scenario-based questions"""
        # Similar to open-ended but with higher weight for thoughtful responses
        base_score = ScoringEngine._score_open_ended(question, response)
        return min(base_score * 1.2, 1.0)  # Boost score but cap at 1.0
    
    @staticmethod
    def _score_personality_test(question: AssessmentQuestion, response: AssessmentResponse) -> float:
        """Score personality test questions"""
        # Personality tests typically don't have right/wrong answers
        # Score based on completion and thoughtfulness
        if response.answer:
            return 1.0
        return 0.0
    
    @staticmethod
    def calculate_overall_progress(assessments: List[StepAssessment]) -> ProgressMetrics:
        """Calculate overall progress metrics across all assessments"""
        if not assessments:
            return ProgressMetrics()
        
        total_weighted_score = 0.0
        total_weight = 0.0
        steps_completed = 0
        total_time_spent = 0
        
        for assessment in assessments:
            if assessment.is_completed:
                step_weight = ScoringEngine.STEP_WEIGHTS.get(assessment.step_type, 1.0)
                total_weighted_score += assessment.total_score * step_weight
                total_weight += step_weight
                steps_completed += 1
        
        # Calculate overall score
        overall_score = (total_weighted_score / total_weight) if total_weight > 0 else 0.0
        
        # Calculate completion percentage
        completion_percentage = (steps_completed / len(assessments)) * 100
        
        return ProgressMetrics(
            overall_score=overall_score,
            steps_completed=steps_completed,
            total_steps=len(assessments),
            completion_percentage=completion_percentage,
            time_spent_minutes=total_time_spent
        )
    
    @staticmethod
    def calculate_career_matches(
        assessments: List[StepAssessment], 
        career_domains: List[CareerDomain]
    ) -> List[CareerDomain]:
        """Calculate career domain matches based on assessment responses"""
        if not assessments or not career_domains:
            return []
        
        # Extract key insights from assessments
        insights = ScoringEngine._extract_insights(assessments)
        
        # Calculate match scores for each career domain
        for domain in career_domains:
            match_score = ScoringEngine._calculate_domain_match(domain, insights)
            domain.match_score = match_score
            domain.confidence_level = ScoringEngine._calculate_confidence_level(match_score, insights)
            domain.reasoning = ScoringEngine._generate_match_reasoning(domain, insights)
        
        # Sort by match score and return top matches
        sorted_domains = sorted(career_domains, key=lambda x: x.match_score, reverse=True)
        return sorted_domains
    
    @staticmethod
    def _extract_insights(assessments: List[StepAssessment]) -> Dict[str, Any]:
        """Extract key insights from assessment responses"""
        insights = {
            "interests": [],
            "skills": [],
            "values": [],
            "personality": [],
            "goals": []
        }
        
        for assessment in assessments:
            if assessment.step_type == StepType.INTERESTS_STRENGTHS:
                for response in assessment.responses:
                    if "interests" in response.question_id:
                        insights["interests"].append(response.answer)
                    elif "strengths" in response.question_id:
                        insights["skills"].append(response.answer)
            
            elif assessment.step_type == StepType.VALUES_PREFERENCES:
                for response in assessment.responses:
                    if "values" in response.question_id:
                        insights["values"].append(response.answer)
            
            elif assessment.step_type == StepType.LEARNING_PERSONALITY:
                for response in assessment.responses:
                    if "personality" in response.question_id:
                        insights["personality"].append(response.answer)
            
            elif assessment.step_type == StepType.PASSION_CAREER_FIT:
                for response in assessment.responses:
                    if "passion" in response.question_id or "career_fit" in response.question_id:
                        insights["goals"].append(response.answer)
        
        return insights
    
    @staticmethod
    def _calculate_domain_match(domain: CareerDomain, insights: Dict[str, Any]) -> float:
        """Calculate match score for a specific career domain"""
        match_score = 0.0
        
        # Interest matching
        interest_score = ScoringEngine._calculate_interest_match(domain, insights["interests"])
        match_score += interest_score * ScoringEngine.CAREER_MATCH_WEIGHTS["interests"]
        
        # Skill matching
        skill_score = ScoringEngine._calculate_skill_match(domain, insights["skills"])
        match_score += skill_score * ScoringEngine.CAREER_MATCH_WEIGHTS["skills"]
        
        # Values matching
        values_score = ScoringEngine._calculate_values_match(domain, insights["values"])
        match_score += values_score * ScoringEngine.CAREER_MATCH_WEIGHTS["values"]
        
        # Personality matching
        personality_score = ScoringEngine._calculate_personality_match(domain, insights["personality"])
        match_score += personality_score * ScoringEngine.CAREER_MATCH_WEIGHTS["personality"]
        
        # Goals matching
        goals_score = ScoringEngine._calculate_goals_match(domain, insights["goals"])
        match_score += goals_score * ScoringEngine.CAREER_MATCH_WEIGHTS["goals"]
        
        return min(match_score * 100, 100.0)  # Convert to 0-100 scale
    
    @staticmethod
    def _calculate_interest_match(domain: CareerDomain, interests: List[str]) -> float:
        """Calculate interest match score"""
        if not interests:
            return 0.0
        
        # Simple keyword matching for now
        domain_keywords = domain.title.lower().split() + domain.description.lower().split()
        interest_keywords = []
        for interest in interests:
            interest_keywords.extend(str(interest).lower().split())
        
        matches = sum(1 for keyword in interest_keywords if keyword in domain_keywords)
        return min(matches / len(interest_keywords), 1.0) if interest_keywords else 0.0
    
    @staticmethod
    def _calculate_skill_match(domain: CareerDomain, skills: List[str]) -> float:
        """Calculate skill match score"""
        if not skills:
            return 0.0
        
        domain_skills = [skill.lower() for skill in domain.required_skills]
        user_skills = [str(skill).lower() for skill in skills]
        
        matches = sum(1 for skill in user_skills if skill in domain_skills)
        return min(matches / len(domain_skills), 1.0) if domain_skills else 0.0
    
    @staticmethod
    def _calculate_values_match(domain: CareerDomain, values: List[str]) -> float:
        """Calculate values match score"""
        # This would require more sophisticated analysis
        # For now, return a moderate score
        return 0.6
    
    @staticmethod
    def _calculate_personality_match(domain: CareerDomain, personality: List[str]) -> float:
        """Calculate personality match score"""
        # This would require personality mapping to career requirements
        # For now, return a moderate score
        return 0.5
    
    @staticmethod
    def _calculate_goals_match(domain: CareerDomain, goals: List[str]) -> float:
        """Calculate goals match score"""
        if not goals:
            return 0.0
        
        # Simple keyword matching
        domain_keywords = domain.title.lower().split() + domain.description.lower().split()
        goal_keywords = []
        for goal in goals:
            goal_keywords.extend(str(goal).lower().split())
        
        matches = sum(1 for keyword in goal_keywords if keyword in domain_keywords)
        return min(matches / len(goal_keywords), 1.0) if goal_keywords else 0.0
    
    @staticmethod
    def _calculate_confidence_level(match_score: float, insights: Dict[str, Any]) -> float:
        """Calculate confidence level based on match score and available data"""
        # Base confidence on match score and data completeness
        data_completeness = sum(len(data) for data in insights.values()) / 20.0  # Normalize to 0-1
        confidence = (match_score / 100.0) * 0.7 + data_completeness * 0.3
        return min(confidence, 1.0)
    
    @staticmethod
    def _generate_match_reasoning(domain: CareerDomain, insights: Dict[str, Any]) -> str:
        """Generate reasoning for career domain match"""
        reasoning_parts = []
        
        if insights["interests"]:
            reasoning_parts.append(f"Your interests in {', '.join(insights['interests'][:2])} align well with this field.")
        
        if insights["skills"]:
            reasoning_parts.append(f"Your strengths in {', '.join(insights['skills'][:2])} are valuable for this career.")
        
        if insights["goals"]:
            reasoning_parts.append(f"Your career goals related to {', '.join(insights['goals'][:1])} match this pathway.")
        
        if not reasoning_parts:
            reasoning_parts.append("This career path shows potential based on your overall assessment profile.")
        
        return " ".join(reasoning_parts)
    
    @staticmethod
    def generate_learning_recommendations(
        career_domains: List[CareerDomain],
        progress: ProgressMetrics
    ) -> List[Dict[str, Any]]:
        """Generate personalized learning recommendations"""
        recommendations = []
        
        # Top career match recommendations
        top_domains = career_domains[:3]
        for domain in top_domains:
            recommendations.append({
                "type": "career_exploration",
                "title": f"Explore {domain.title}",
                "description": f"Learn more about {domain.title} and its requirements",
                "priority": "high" if domain.match_score > 80 else "medium",
                "estimated_time": "2-4 hours",
                "resources": ["Online research", "Professional networking", "Informational interviews"]
            })
        
        # Skill development recommendations
        if progress.overall_score < 70:
            recommendations.append({
                "type": "skill_development",
                "title": "Strengthen Core Skills",
                "description": "Focus on developing fundamental skills identified in your assessments",
                "priority": "high",
                "estimated_time": "10-20 hours",
                "resources": ["Online courses", "Practice exercises", "Skill assessments"]
            })
        
        # Education pathway recommendations
        recommendations.append({
            "type": "education_planning",
            "title": "Research Education Options",
            "description": "Investigate educational pathways for your top career choices",
            "priority": "medium",
            "estimated_time": "5-10 hours",
            "resources": ["University websites", "Program catalogs", "Student testimonials"]
        })
        
        return recommendations 