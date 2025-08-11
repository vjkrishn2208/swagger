from typing import Dict, List, Any
from models.session_models import (
    StepType, AssessmentType, AssessmentQuestion, 
    CareerDomain, LearningPathway, ActionItem
)

class CVPStepContent:
    """Contains all the content, assessments, and prompts for the CVP Lite program steps"""
    
    @staticmethod
    def get_step_content(step_type: StepType, language: str = "en") -> Dict[str, Any]:
        """Get the content for a specific step"""
        content_map = {
            StepType.PROFILE_SETUP: CVPStepContent._get_profile_setup_content(language),
            StepType.INTERESTS_STRENGTHS: CVPStepContent._get_interests_strengths_content(language),
            StepType.VALUES_PREFERENCES: CVPStepContent._get_values_preferences_content(language),
            StepType.LEARNING_PERSONALITY: CVPStepContent._get_learning_personality_content(language),
            StepType.PASSION_CAREER_FIT: CVPStepContent._get_passion_career_fit_content(language),
            StepType.COGNITIVE_THINKING: CVPStepContent._get_cognitive_thinking_content(language),
            StepType.EMOTIONAL_ETHICAL: CVPStepContent._get_emotional_ethical_content(language),
            StepType.CAREER_SUMMARY: CVPStepContent._get_career_summary_content(language),
            StepType.EDUCATION_PATHWAYS: CVPStepContent._get_education_pathways_content(language),
            StepType.ACTION_PLAN: CVPStepContent._get_action_plan_content(language),
        }
        return content_map.get(step_type, {})
    
    @staticmethod
    def _get_profile_setup_content(language: str) -> Dict[str, Any]:
        return {
            "title": "Candidate Profile Setup",
            "description": "Let's start by understanding your basic information and background",
            "prompt": "Please tell us about yourself and your current situation",
            "assessment": {
                "questions": [
                    AssessmentQuestion(
                        id="profile_1",
                        question="What is your current education level?",
                        type=AssessmentType.MULTIPLE_CHOICE,
                        options=["High School", "Some College", "Bachelor's Degree", "Master's Degree", "PhD", "Other"],
                        required=True,
                        weight=1.0
                    ),
                    AssessmentQuestion(
                        id="profile_2",
                        question="What is your age?",
                        type=AssessmentType.SCALE_RATING,
                        scale_min=13,
                        scale_max=100,
                        required=True,
                        weight=1.0
                    ),
                    AssessmentQuestion(
                        id="profile_3",
                        question="What subjects or topics interest you the most?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=1.5
                    ),
                    AssessmentQuestion(
                        id="profile_4",
                        question="What are your current career goals or aspirations?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=2.0
                    )
                ]
            }
        }
    
    @staticmethod
    def _get_interests_strengths_content(language: str) -> Dict[str, Any]:
        return {
            "title": "Interest & Strengths Discovery",
            "description": "Let's explore what truly interests you and where your strengths lie",
            "prompt": "Think about activities, subjects, and skills that energize you",
            "assessment": {
                "questions": [
                    AssessmentQuestion(
                        id="interests_1",
                        question="Which of these activities would you most enjoy doing?",
                        type=AssessmentType.MULTIPLE_CHOICE,
                        options=["Solving complex problems", "Creating artistic content", "Helping others", "Building things", "Analyzing data", "Leading teams"],
                        required=True,
                        weight=1.5
                    ),
                    AssessmentQuestion(
                        id="interests_2",
                        question="What subjects did you enjoy most in school?",
                        type=AssessmentType.MULTIPLE_CHOICE,
                        options=["Mathematics", "Science", "Literature", "History", "Arts", "Physical Education", "Technology"],
                        required=True,
                        weight=1.0
                    ),
                    AssessmentQuestion(
                        id="strengths_1",
                        question="Rate your confidence in these areas (1-10):",
                        type=AssessmentType.SCALE_RATING,
                        scale_min=1,
                        scale_max=10,
                        required=True,
                        weight=1.0
                    ),
                    AssessmentQuestion(
                        id="strengths_2",
                        question="What skills do you think you're naturally good at?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=1.5
                    )
                ]
            }
        }
    
    @staticmethod
    def _get_values_preferences_content(language: str) -> Dict[str, Any]:
        return {
            "title": "Values & Preferences Discovery",
            "description": "Understanding what matters most to you in life and work",
            "prompt": "Consider what values and preferences guide your decisions",
            "assessment": {
                "questions": [
                    AssessmentQuestion(
                        id="values_1",
                        question="What is most important to you in a career?",
                        type=AssessmentType.MULTIPLE_CHOICE,
                        options=["Making a positive impact", "Financial security", "Creative freedom", "Work-life balance", "Continuous learning", "Recognition"],
                        required=True,
                        weight=2.0
                    ),
                    AssessmentQuestion(
                        id="values_2",
                        question="How do you prefer to work?",
                        type=AssessmentType.MULTIPLE_CHOICE,
                        options=["Independently", "In small teams", "In large organizations", "Remotely", "In person", "Flexible"],
                        required=True,
                        weight=1.5
                    ),
                    AssessmentQuestion(
                        id="preferences_1",
                        question="What work environment appeals to you most?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=1.0
                    )
                ]
            }
        }
    
    @staticmethod
    def _get_learning_personality_content(language: str) -> Dict[str, Any]:
        return {
            "title": "Learning Style & Personality Assessment",
            "description": "Discovering how you learn best and understanding your personality traits",
            "prompt": "Reflect on how you prefer to learn and interact with others",
            "assessment": {
                "questions": [
                    AssessmentQuestion(
                        id="learning_1",
                        question="How do you prefer to learn new things?",
                        type=AssessmentType.MULTIPLE_CHOICE,
                        options=["Reading and research", "Hands-on practice", "Visual demonstrations", "Group discussions", "One-on-one instruction"],
                        required=True,
                        weight=1.5
                    ),
                    AssessmentQuestion(
                        id="personality_1",
                        question="How would you describe your personality?",
                        type=AssessmentType.MULTIPLE_CHOICE,
                        options=["Introverted", "Extroverted", "Analytical", "Creative", "Organized", "Spontaneous"],
                        required=True,
                        weight=1.0
                    ),
                    AssessmentQuestion(
                        id="personality_2",
                        question="Rate your comfort level with change (1-10):",
                        type=AssessmentType.SCALE_RATING,
                        scale_min=1,
                        scale_max=10,
                        required=True,
                        weight=1.0
                    )
                ]
            }
        }
    
    @staticmethod
    def _get_passion_career_fit_content(language: str) -> Dict[str, Any]:
        return {
            "title": "Passion & Career Fit Analysis",
            "description": "Connecting your passions with potential career paths",
            "prompt": "Think about what excites you and how it could translate into a career",
            "assessment": {
                "questions": [
                    AssessmentQuestion(
                        id="passion_1",
                        question="What topics could you talk about for hours?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=2.0
                    ),
                    AssessmentQuestion(
                        id="passion_2",
                        question="What problems in the world would you like to solve?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=2.0
                    ),
                    AssessmentQuestion(
                        id="career_fit_1",
                        question="Which of these career areas interests you most?",
                        type=AssessmentType.MULTIPLE_CHOICE,
                        options=["Technology & Innovation", "Healthcare & Wellness", "Education & Training", "Business & Finance", "Arts & Media", "Science & Research", "Social Impact"],
                        required=True,
                        weight=1.5
                    )
                ]
            }
        }
    
    @staticmethod
    def _get_cognitive_thinking_content(language: str) -> Dict[str, Any]:
        return {
            "title": "Cognitive Thinking Scenario Assessment",
            "description": "Evaluating your problem-solving and critical thinking abilities",
            "prompt": "Let's explore how you approach complex problems and decisions",
            "assessment": {
                "questions": [
                    AssessmentQuestion(
                        id="cognitive_1",
                        question="How do you typically approach a complex problem?",
                        type=AssessmentType.MULTIPLE_CHOICE,
                        options=["Break it down into smaller parts", "Research similar problems", "Ask for help from experts", "Try different approaches", "Analyze all possible outcomes"],
                        required=True,
                        weight=1.5
                    ),
                    AssessmentQuestion(
                        id="cognitive_2",
                        question="Rate your ability to think logically (1-10):",
                        type=AssessmentType.SCALE_RATING,
                        scale_min=1,
                        scale_max=10,
                        required=True,
                        weight=1.0
                    ),
                    AssessmentQuestion(
                        id="cognitive_3",
                        question="Describe a time when you had to think creatively to solve a problem:",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=2.0
                    )
                ]
            }
        }
    
    @staticmethod
    def _get_emotional_ethical_content(language: str) -> Dict[str, Any]:
        return {
            "title": "Emotional & Ethical Intelligence",
            "description": "Understanding your emotional awareness and ethical decision-making",
            "prompt": "Reflect on how you handle emotions and make ethical choices",
            "assessment": {
                "questions": [
                    AssessmentQuestion(
                        id="emotional_1",
                        question="How do you handle stress and pressure?",
                        type=AssessmentType.MULTIPLE_CHOICE,
                        options=["Take deep breaths and stay calm", "Talk to someone about it", "Exercise or physical activity", "Take a break and return later", "Make a plan to address it"],
                        required=True,
                        weight=1.5
                    ),
                    AssessmentQuestion(
                        id="ethical_1",
                        question="How do you make decisions when faced with ethical dilemmas?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=2.0
                    ),
                    AssessmentQuestion(
                        id="emotional_2",
                        question="Rate your ability to understand others' emotions (1-10):",
                        type=AssessmentType.SCALE_RATING,
                        scale_min=1,
                        scale_max=10,
                        required=True,
                        weight=1.0
                    )
                ]
            }
        }
    
    @staticmethod
    def _get_career_summary_content(language: str) -> Dict[str, Any]:
        return {
            "title": "Career Summary & Direction Bridge",
            "description": "Synthesizing all assessments to identify your career direction",
            "prompt": "Based on what we've discovered, let's summarize your career path",
            "assessment": {
                "questions": [
                    AssessmentQuestion(
                        id="summary_1",
                        question="What career path feels most aligned with your assessments?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=2.0
                    ),
                    AssessmentQuestion(
                        id="summary_2",
                        question="What excites you most about this career direction?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=1.5
                    ),
                    AssessmentQuestion(
                        id="summary_3",
                        question="What concerns or questions do you have about this path?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=1.0
                    )
                ]
            }
        }
    
    @staticmethod
    def _get_education_pathways_content(language: str) -> Dict[str, Any]:
        return {
            "title": "Education Pathways & College Strategy",
            "description": "Mapping out the educational journey to your career goals",
            "prompt": "Let's explore the educational paths that can lead to your chosen career",
            "assessment": {
                "questions": [
                    AssessmentQuestion(
                        id="education_1",
                        question="What type of education do you prefer?",
                        type=AssessmentType.MULTIPLE_CHOICE,
                        options=["Traditional university", "Online learning", "Vocational training", "Apprenticeship", "Self-directed learning", "Hybrid approach"],
                        required=True,
                        weight=1.5
                    ),
                    AssessmentQuestion(
                        id="education_2",
                        question="What is your timeline for completing education?",
                        type=AssessmentType.MULTIPLE_CHOICE,
                        options=["1-2 years", "3-4 years", "5+ years", "Flexible timeline"],
                        required=True,
                        weight=1.0
                    ),
                    AssessmentQuestion(
                        id="education_3",
                        question="What factors are most important in choosing an educational institution?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=1.5
                    )
                ]
            }
        }
    
    @staticmethod
    def _get_action_plan_content(language: str) -> Dict[str, Any]:
        return {
            "title": "Personal Action Plan Framework",
            "description": "Creating a concrete plan to achieve your career goals",
            "prompt": "Let's develop specific actions you can take to move forward",
            "assessment": {
                "questions": [
                    AssessmentQuestion(
                        id="action_1",
                        question="What is your first immediate action step?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=2.0
                    ),
                    AssessmentQuestion(
                        id="action_2",
                        question="What is your timeline for achieving your career goal?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=1.5
                    ),
                    AssessmentQuestion(
                        id="action_3",
                        question="What resources or support do you need?",
                        type=AssessmentType.OPEN_ENDED,
                        required=True,
                        weight=1.0
                    )
                ]
            }
        }
    
    @staticmethod
    def get_career_domains() -> List[CareerDomain]:
        """Get predefined career domains for recommendations"""
        return [
            CareerDomain(
                id="tech_software",
                title="Software Development",
                description="Creating applications, websites, and software solutions",
                match_score=0.0,
                confidence_level=0.0,
                reasoning="",
                required_skills=["Programming", "Problem Solving", "Logic", "Creativity"],
                growth_potential="High",
                salary_range="$60,000 - $150,000+"
            ),
            CareerDomain(
                id="tech_data",
                title="Data Science & Analytics",
                description="Analyzing data to drive business decisions and insights",
                match_score=0.0,
                confidence_level=0.0,
                reasoning="",
                required_skills=["Statistics", "Programming", "Critical Thinking", "Communication"],
                growth_potential="Very High",
                salary_range="$70,000 - $160,000+"
            ),
            CareerDomain(
                id="healthcare",
                title="Healthcare & Medicine",
                description="Providing medical care and improving patient health",
                match_score=0.0,
                confidence_level=0.0,
                reasoning="",
                required_skills=["Science", "Compassion", "Attention to Detail", "Communication"],
                growth_potential="High",
                salary_range="$50,000 - $200,000+"
            ),
            CareerDomain(
                id="business",
                title="Business & Management",
                description="Leading organizations and driving business success",
                match_score=0.0,
                confidence_level=0.0,
                reasoning="",
                required_skills=["Leadership", "Communication", "Strategic Thinking", "Problem Solving"],
                growth_potential="High",
                salary_range="$50,000 - $200,000+"
            ),
            CareerDomain(
                id="creative",
                title="Creative Arts & Design",
                description="Expressing creativity through visual, digital, and performing arts",
                match_score=0.0,
                confidence_level=0.0,
                reasoning="",
                required_skills=["Creativity", "Technical Skills", "Communication", "Adaptability"],
                growth_potential="Medium-High",
                salary_range="$30,000 - $120,000+"
            ),
            CareerDomain(
                id="education",
                title="Education & Training",
                description="Teaching and developing others' knowledge and skills",
                match_score=0.0,
                confidence_level=0.0,
                reasoning="",
                required_skills=["Communication", "Patience", "Knowledge", "Adaptability"],
                growth_potential="Medium",
                salary_range="$40,000 - $100,000+"
            ),
            CareerDomain(
                id="science",
                title="Scientific Research",
                description="Advancing knowledge through research and discovery",
                match_score=0.0,
                confidence_level=0.0,
                reasoning="",
                required_skills=["Research Skills", "Analytical Thinking", "Curiosity", "Persistence"],
                growth_potential="Medium-High",
                salary_range="$50,000 - $120,000+"
            ),
            CareerDomain(
                id="social_impact",
                title="Social Impact & Non-Profit",
                description="Making positive change in communities and society",
                match_score=0.0,
                confidence_level=0.0,
                reasoning="",
                required_skills=["Passion", "Communication", "Organization", "Empathy"],
                growth_potential="Medium",
                salary_range="$30,000 - $80,000+"
            )
        ]
    
    @staticmethod
    def get_learning_pathways() -> List[LearningPathway]:
        """Get predefined learning pathways for different career domains"""
        return [
            LearningPathway(
                id="cs_degree",
                title="Computer Science Degree",
                description="Traditional 4-year university program in computer science",
                duration="4 years",
                cost_range="$20,000 - $200,000",
                institutions=["Universities worldwide"],
                prerequisites=["High school diploma, Math skills"],
                career_outcomes=["Software Developer", "Data Scientist", "Systems Analyst"]
            ),
            LearningPathway(
                id="coding_bootcamp",
                title="Coding Bootcamp",
                description="Intensive, focused programming training program",
                duration="3-6 months",
                cost_range="$5,000 - $20,000",
                institutions=["General Assembly", "Flatiron School", "Le Wagon"],
                prerequisites=["Basic computer skills, dedication"],
                career_outcomes=["Web Developer", "Software Developer", "Data Analyst"]
            ),
            LearningPathway(
                id="online_courses",
                title="Online Learning Platforms",
                description="Self-paced online courses and certifications",
                duration="Flexible",
                cost_range="$0 - $500 per course",
                institutions=["Coursera", "Udemy", "edX", "freeCodeCamp"],
                prerequisites=["Internet access, self-discipline"],
                career_outcomes=["Various tech roles", "Skill development"]
            ),
            LearningPathway(
                id="apprenticeship",
                title="Apprenticeship Program",
                description="Learning while working under experienced professionals",
                duration="1-4 years",
                cost_range="$0 - $10,000",
                institutions=["Companies with apprenticeship programs"],
                prerequisites=["High school diploma, willingness to learn"],
                career_outcomes=["Skilled trades", "Technical roles"]
            )
        ] 