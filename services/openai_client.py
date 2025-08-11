import openai
from app_config import settings
from typing import Optional, Dict, Any
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = settings.OPENAI_API_KEY

async def generate_completion(
    prompt: str, 
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    model: Optional[str] = None
) -> str:
    """
    Generate text completion using OpenAI API
    
    Args:
        prompt: The input prompt
        max_tokens: Maximum tokens to generate (defaults to config)
        temperature: Creativity level 0-2 (defaults to config)
        model: Model to use (defaults to config)
    
    Returns:
        Generated text response
    """
    try:
        # Use configured defaults if not specified
        max_tokens = max_tokens or settings.OPENAI_MAX_TOKENS
        temperature = temperature or settings.OPENAI_TEMPERATURE
        model = model or settings.OPENAI_MODEL
        
        # Create completion request
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI career mentor for the CVP Lite program."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        # Extract and return the response
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            logger.warning("OpenAI API returned no choices")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
            
    except openai.error.AuthenticationError:
        logger.error("OpenAI API authentication failed. Check your API key.")
        return "I'm experiencing technical difficulties. Please check your configuration."
        
    except openai.error.RateLimitError:
        logger.error("OpenAI API rate limit exceeded.")
        return "I'm receiving too many requests right now. Please wait a moment and try again."
        
    except openai.error.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        return "I'm experiencing technical difficulties. Please try again later."
        
    except Exception as e:
        logger.error(f"Unexpected error in OpenAI client: {e}")
        return "I'm having trouble processing your request. Please try again."

async def generate_assessment_analysis(
    question: str,
    response: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate analysis of assessment responses
    
    Args:
        question: The assessment question
        response: Student's response
        context: Additional context about the assessment
    
    Returns:
        Analysis results including feedback and insights
    """
    prompt = f"""
    Analyze this assessment response:
    
    Question: {question}
    Student Response: {response}
    Context: {context}
    
    Provide analysis in this format:
    - Feedback: [Encouraging feedback on the response]
    - Insights: [Key insights about the student's thinking]
    - Career Connections: [How this relates to career possibilities]
    - Next Questions: [Suggestions for follow-up questions]
    
    Keep the tone encouraging and constructive.
    """
    
    try:
        analysis_text = await generate_completion(prompt, max_tokens=300)
        
        # Parse the analysis (simple parsing for now)
        analysis = {
            "feedback": "",
            "insights": "",
            "career_connections": "",
            "next_questions": []
        }
        
        # Simple parsing of the response
        lines = analysis_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('- Feedback:'):
                current_section = 'feedback'
                analysis['feedback'] = line.replace('- Feedback:', '').strip()
            elif line.startswith('- Insights:'):
                current_section = 'insights'
                analysis['insights'] = line.replace('- Insights:', '').strip()
            elif line.startswith('- Career Connections:'):
                current_section = 'career_connections'
                analysis['career_connections'] = line.replace('- Career Connections:', '').strip()
            elif line.startswith('- Next Questions:'):
                current_section = 'next_questions'
            elif current_section == 'next_questions' and line.startswith('-'):
                question_text = line.replace('-', '').strip()
                if question_text:
                    analysis['next_questions'].append(question_text)
            elif current_section and line and not line.startswith('-'):
                # Continue building the current section
                if current_section in analysis:
                    analysis[current_section] += ' ' + line
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error generating assessment analysis: {e}")
        return {
            "feedback": "Thank you for sharing that response. It provides valuable insight into your thinking.",
            "insights": "Your response shows thoughtful consideration of the question.",
            "career_connections": "This type of reflection is important for career decision-making.",
            "next_questions": ["Could you tell me more about that?", "What led you to that conclusion?"]
        }

async def generate_career_recommendations(
    student_profile: Dict[str, Any],
    assessment_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate personalized career recommendations
    
    Args:
        student_profile: Student's background information
        assessment_results: Results from various assessments
    
    Returns:
        Career recommendations and insights
    """
    prompt = f"""
    Based on this student profile and assessment results, generate career recommendations:
    
    Student Profile: {student_profile}
    Assessment Results: {assessment_results}
    
    Provide recommendations in this format:
    - Top Career Matches: [3-5 career paths with reasoning]
    - Skill Development: [Areas to focus on for career success]
    - Education Pathways: [Recommended educational approaches]
    - Action Steps: [Immediate next steps to take]
    - Long-term Vision: [Career vision for the next 5-10 years]
    
    Be specific, encouraging, and actionable.
    """
    
    try:
        recommendations_text = await generate_completion(prompt, max_tokens=500)
        
        # Parse recommendations (simple parsing for now)
        recommendations = {
            "top_career_matches": [],
            "skill_development": [],
            "education_pathways": [],
            "action_steps": [],
            "long_term_vision": ""
        }
        
        # Simple parsing logic
        lines = recommendations_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('- Top Career Matches:'):
                current_section = 'top_career_matches'
            elif line.startswith('- Skill Development:'):
                current_section = 'skill_development'
            elif line.startswith('- Education Pathways:'):
                current_section = 'education_pathways'
            elif line.startswith('- Action Steps:'):
                current_section = 'action_steps'
            elif line.startswith('- Long-term Vision:'):
                current_section = 'long_term_vision'
            elif current_section and line.startswith('-'):
                item = line.replace('-', '').strip()
                if current_section in ['top_career_matches', 'skill_development', 'education_pathways', 'action_steps']:
                    if item:
                        recommendations[current_section].append(item)
            elif current_section == 'long_term_vision' and line and not line.startswith('-'):
                recommendations['long_term_vision'] += ' ' + line
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating career recommendations: {e}")
        return {
            "top_career_matches": ["Continue exploring your interests to find the best career fit"],
            "skill_development": ["Focus on building both technical and soft skills"],
            "education_pathways": ["Research educational options that align with your goals"],
            "action_steps": ["Complete the full assessment to get more specific guidance"],
            "long_term_vision": "Your career path will become clearer as you complete more assessments and gain self-awareness."
        }