#!/usr/bin/env python3
"""
Test script for LLM integration and text evaluation
"""

import sys
import os
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.append(backend_path)

# Change to backend directory for proper config path resolution
original_cwd = os.getcwd()
os.chdir(backend_path)

from services.llm_service import get_llm_service, evaluate_text_with_llm

def test_llm_service_initialization():
    """Test LLM service initialization"""
    print("Testing LLM service initialization...")
    
    try:
        llm_service = get_llm_service()
        print("✅ LLM service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ LLM service initialization failed: {e}")
        return False

def test_llm_health_check():
    """Test LLM health check"""
    print("Testing LLM health check...")
    
    try:
        llm_service = get_llm_service()
        health_data = llm_service.health_check()
        
        if health_data["status"] == "healthy":
            print("✅ LLM health check passed")
            print(f"   Provider: {health_data.get('provider', 'N/A')}")
            print(f"   Model: {health_data.get('model', 'N/A')}")
            print(f"   API Accessible: {health_data.get('api_accessible', False)}")
            return True
        else:
            print(f"❌ LLM health check failed: {health_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ LLM health check failed: {e}")
        return False

def test_text_evaluation():
    """Test text evaluation functionality"""
    print("Testing text evaluation...")
    
    # Sample text for testing
    test_text = """
    Executive Summary
    
    We propose investing $2.5 million in a new patient management system to improve operational efficiency and patient outcomes. The system will integrate with existing electronic health records and provide real-time analytics for better decision-making.
    
    The investment will generate an estimated ROI of 25% over three years, with payback period of 18 months. Key benefits include reduced administrative overhead, improved patient satisfaction, and better compliance with healthcare regulations.
    
    Implementation will require 6 months with minimal disruption to current operations. We have identified key risks including data migration challenges and user adoption, but have mitigation strategies in place.
    """
    
    try:
        success, evaluation_data, error = evaluate_text_with_llm(test_text)
        
        if success:
            print("✅ Text evaluation completed successfully")
            print(f"   Overall Score: {evaluation_data.get('overall_score', 'N/A')}")
            print(f"   Processing Time: {evaluation_data.get('processing_time', 'N/A')} seconds")
            print(f"   Model Used: {evaluation_data.get('model_used', 'N/A')}")
            
            # Check for required fields
            required_fields = ['overall_score', 'strengths', 'opportunities', 'rubric_scores']
            missing_fields = [field for field in required_fields if field not in evaluation_data]
            
            if missing_fields:
                print(f"   ⚠️ Missing fields: {missing_fields}")
            else:
                print("   ✅ All required fields present")
            
            return True
        else:
            print(f"❌ Text evaluation failed: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Text evaluation failed: {e}")
        return False

def test_error_handling():
    """Test error handling for invalid inputs"""
    print("Testing error handling...")
    
    # Test empty text
    try:
        success, evaluation_data, error = evaluate_text_with_llm("")
        
        if not success and "required" in error.lower():
            print("✅ Empty text validation working")
        else:
            print("❌ Empty text validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Empty text test failed: {e}")
        return False
    
    # Test very long text
    try:
        long_text = "A" * 15000  # Exceeds 10,000 character limit
        success, evaluation_data, error = evaluate_text_with_llm(long_text)
        
        if not success and "length" in error.lower():
            print("✅ Text length validation working")
        else:
            print("❌ Text length validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Long text test failed: {e}")
        return False
    
    return True

def main():
    """Run all LLM tests"""
    print("🧪 Testing Memo AI Coach LLM Integration")
    print("=" * 50)
    
    # Test 1: Service Initialization
    init_ok = test_llm_service_initialization()
    
    # Test 2: Health Check (only if initialization works)
    health_ok = False
    if init_ok:
        health_ok = test_llm_health_check()
    
    # Test 3: Text Evaluation (only if health check works)
    eval_ok = False
    if health_ok:
        eval_ok = test_text_evaluation()
    
    # Test 4: Error Handling
    error_ok = test_error_handling()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Service Initialization: {'✅ PASS' if init_ok else '❌ FAIL'}")
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Text Evaluation: {'✅ PASS' if eval_ok else '❌ FAIL'}")
    print(f"Error Handling: {'✅ PASS' if error_ok else '❌ FAIL'}")
    
    # Restore original working directory
    os.chdir(original_cwd)
    
    if init_ok and health_ok and eval_ok and error_ok:
        print("\n🎉 All tests passed! LLM integration is working.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check LLM configuration and API key.")
        return 1

if __name__ == "__main__":
    exit(main())
