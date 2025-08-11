#!/usr/bin/env python3
"""
Test script for CVP Lite system
This script tests the major components to ensure they're working correctly
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_models():
    """Test that all models can be imported and instantiated"""
    print("Testing Models...")
    
    try:
        from models.session_models import (
            StepType, Language, Tier, AssessmentType,
            StartSessionRequest, StepRequest, StepResponse
        )
        
        # Test enum values
        assert StepType.PROFILE_SETUP.value == "profile_setup"
        assert Language.ENGLISH.value == "en"
        assert Tier.BASIC.value == "basic"
        assert AssessmentType.MULTIPLE_CHOICE.value == "multiple_choice"
        
        # Test model instantiation
        start_request = StartSessionRequest(
            student_id="test_student",
            language=Language.ENGLISH,
            tier=Tier.BASIC
        )
        
        step_request = StepRequest(
            session_id="test_session",
            step_type=StepType.PROFILE_SETUP
        )
        
        print(" Models test passed")
        return True
        
    except Exception as e:
        print(f" Models test failed: {e}")
        return False

async def test_services():
    """Test that all services can be imported and basic functions work"""
    print("Testing Services...")
    
    try:
        # Test CVP Step Content
        from services.cvp_step_content import CVPStepContent
        from models.session_models import StepType
        
        content = CVPStepContent.get_step_content(StepType.PROFILE_SETUP)
        assert "title" in content
        assert "assessment" in content
        
        career_domains = CVPStepContent.get_career_domains()
        assert len(career_domains) > 0
        
        learning_pathways = CVPStepContent.get_learning_pathways()
        assert len(learning_pathways) > 0
        
        # Test Scoring Engine
        from services.scoring_engine import ScoringEngine
        from models.session_models import StepAssessment, AssessmentQuestion, AssessmentResponse
        
        # Create a simple assessment for testing
        question = AssessmentQuestion(
            id="test_1",
            question="Test question?",
            type=AssessmentType.MULTIPLE_CHOICE,
            options=["Yes", "No"],
            required=True,
            weight=1.0
        )
        
        response = AssessmentResponse(
            question_id="test_1",
            answer="Yes"
        )
        
        assessment = StepAssessment(
            step_type=StepType.PROFILE_SETUP,
            questions=[question],
            responses=[response]
        )
        
        # Test scoring
        score, max_score, completion = ScoringEngine.calculate_assessment_score(assessment)
        assert score >= 0
        assert completion >= 0
        
        print("✅ Services test passed")
        return True
        
    except Exception as e:
        print(f"Services test failed: {e}")
        return False

async def test_ai_mentor():
    """Test AI Mentor service"""
    print("🧪 Testing AI Mentor...")
    
    try:
        from services.ai_mentor import AIMentor
        from models.session_models import StepType, Language
        
        # Test step prompt generation
        prompt = await AIMentor.generate_step_prompt(
            StepType.PROFILE_SETUP,
            Language.ENGLISH
        )
        assert len(prompt) > 0
        
        # Test feedback generation
        from models.session_models import AssessmentResponse
        response = AssessmentResponse(
            question_id="profile_1",
            answer="High School"
        )
        
        feedback = await AIMentor.generate_assessment_feedback(
            "profile_1",
            response,
            StepType.PROFILE_SETUP,
            Language.ENGLISH
        )
        assert len(feedback) > 0
        
        print("✅ AI Mentor test passed")
        return True
        
    except Exception as e:
        print(f" AI Mentor test failed: {e}")
        return False

async def test_configuration():
    """Test configuration loading"""
    print("Testing Configuration...")
    
    try:
        from app_config import settings
        
        # Test that settings are loaded
        assert hasattr(settings, 'API_TITLE')
        assert hasattr(settings, 'OPENAI_API_KEY')
        assert hasattr(settings, 'PINECONE_API_KEY')
        assert hasattr(settings, 'MONGO_URI')
        assert hasattr(settings, 'MAX_STEPS')
        
        print(f" Configuration test passed - API Title: {settings.API_TITLE}")
        return True
        
    except Exception as e:
        print(f" Configuration test failed: {e}")
        return False

async def test_database_client():
    """Test database client (without actual connection)"""
    print(" Testing Database Client...")
    
    try:
        from db.mongo_client import (
            get_session, save_session, save_assessment,
            get_assessments, get_career_domains
        )
        
        # Test that functions can be imported
        assert callable(get_session)
        assert callable(save_session)
        assert callable(save_assessment)
        assert callable(get_assessments)
        assert callable(get_career_domains)
        
        print("Database client test passed")
        return True
        
    except Exception as e:
        print(f" Database client test failed: {e}")
        return False

async def test_openai_client():
    """Test OpenAI client (without actual API calls)"""
    print("Testing OpenAI Client...")
    
    try:
        from services.openai_client import (
            generate_completion, generate_assessment_analysis,
            generate_career_recommendations
        )
        
        # Test that functions can be imported
        assert callable(generate_completion)
        assert callable(generate_assessment_analysis)
        assert callable(generate_career_recommendations)
        
        print("OpenAI client test passed")
        return True
        
    except Exception as e:
        print(f" OpenAI client test failed: {e}")
        return False

async def test_pinecone_client():
    """Test Pinecone client (without actual connection)"""
    print(" Testing Pinecone Client...")
    
    try:
        from services.pinecone_client import (
            init_pinecone, create_index, get_index,
            upsert_knowledge_vectors, search_knowledge
        )
        
        # Test that functions can be imported
        assert callable(init_pinecone)
        assert callable(create_index)
        assert callable(get_index)
        assert callable(upsert_knowledge_vectors)
        assert callable(search_knowledge)
        
        print(" Pinecone client test passed")
        return True
        
    except Exception as e:
        print(f" Pinecone client test failed: {e}")
        return False

async def test_controller():
    """Test session controller (without database operations)"""
    print(" Testing Session Controller...")
    
    try:
        from controllers.session_controller import SessionController
        
        # Test that class can be imported
        assert SessionController is not None
        
        # Test helper methods
        step_number = SessionController._get_step_number(StepType.PROFILE_SETUP)
        assert step_number == 1
        
        next_step = SessionController._get_next_step(StepType.PROFILE_SETUP, None)
        assert next_step == StepType.INTERESTS_STRENGTHS
        
        print(" Session controller test passed")
        return True
        
    except Exception as e:
        print(f" Session controller test failed: {e}")
        return False

async def test_routes():
    """Test that routes can be imported"""
    print(" Testing Routes...")
    
    try:
        from routes.session_routes import router
        
        # Test that router can be imported
        assert router is not None
        
        # Check that routes are defined
        routes = [route.path for route in router.routes]
        assert "/start_session" in routes
        assert "/step" in routes
        assert "/session" in routes
        assert "/progress" in routes
        assert "/report" in routes
        
        print(" Routes test passed")
        return True
        
    except Exception as e:
        print(f" Routes test failed: {e}")
        return False

async def test_main_app():
    """Test main app configuration"""
    print("Testing Main App...")
    
    try:
        from app_main import app
        
        # Test that app can be imported
        assert app is not None
        
        # Check app metadata
        assert app.title == "CVP Lite - AI Mentor Backend"
        
        print(" Main app test passed")
        return True
        
    except Exception as e:
        print(f" Main app test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests and report results"""
    print("Starting CVP Lite System Tests...")
    print("=" * 50)
    
    tests = [
        test_models,
        test_services,
        test_ai_mentor,
        test_configuration,
        test_database_client,
        test_openai_client,
        test_pinecone_client,
        test_controller,
        test_routes,
        test_main_app
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f" Test {test.__name__} crashed: {e}")
            results.append(False)
        print()
    
    # Summary
    print("=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print(f" Failed: {total - passed}/{total}")
    
    if passed == total:
        print(" All tests passed! The CVP Lite system is ready to run.")
        return True
    else:
        print("  Some tests failed. Please check the errors above.")
        return False

def main():
    """Main function to run tests"""
    try:
        # Run async tests
        result = asyncio.run(run_all_tests())
        
        if result:
            print("\n System is ready! You can now run:")
            print("uvicorn app_main:app --reload")
            print("\nThen visit: http://localhost:8000/docs")
        else:
            print("\n System has issues that need to be resolved.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 