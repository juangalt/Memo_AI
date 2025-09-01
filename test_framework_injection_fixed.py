#!/usr/bin/env python3
"""
Test script for framework injection implementation (Fixed Version)
"""

import sys
import os
import yaml
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def test_framework_extraction():
    """Test framework extraction from rubric.yaml"""
    print_header("Testing Framework Extraction")
    
    try:
        # Load rubric configuration
        with open('config/rubric.yaml', 'r') as f:
            rubric_config = yaml.safe_load(f)
        
        frameworks = rubric_config.get('frameworks', {})
        framework_definitions = frameworks.get('framework_definitions', {})
        
        if not framework_definitions:
            print_error("No framework definitions found in rubric.yaml")
            return False
        
        print_success(f"Found {len(framework_definitions)} framework definitions")
        
        # Check for expected frameworks
        expected_frameworks = ['pyramid_principle', 'scqa', 'healthcare_investment']
        found_frameworks = []
        
        for framework_key, framework_data in framework_definitions.items():
            print(f"   Framework: {framework_data.get('name', framework_key)}")
            print(f"   Description: {framework_data.get('description', 'No description')[:100]}...")
            print(f"   Application: {framework_data.get('application', 'No application guidance')[:100]}...")
            print()
            found_frameworks.append(framework_key)
        
        # Check if all expected frameworks are present
        missing_frameworks = [f for f in expected_frameworks if f not in found_frameworks]
        if missing_frameworks:
            print_error(f"Missing frameworks: {missing_frameworks}")
            return False
        
        print_success("All expected frameworks found")
        return True
        
    except Exception as e:
        print_error(f"Framework extraction test failed: {e}")
        return False

def test_application_guidance():
    """Test application guidance extraction"""
    print_header("Testing Application Guidance Extraction")
    
    try:
        # Load rubric configuration
        with open('config/rubric.yaml', 'r') as f:
            rubric_config = yaml.safe_load(f)
        
        frameworks = rubric_config.get('frameworks', {})
        application_guidance = frameworks.get('application_guidance', {})
        
        if not application_guidance:
            print_error("No application guidance found in rubric.yaml")
            return False
        
        print_success("Application guidance found")
        
        # Check for expected guidance sections
        expected_sections = ['overall_evaluation', 'scoring_evaluation', 'segment_evaluation', 'domain_focus']
        
        for section in expected_sections:
            if section in application_guidance:
                print_success(f"Found {section}: {application_guidance[section][:100]}...")
            else:
                print_error(f"Missing {section} section")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Application guidance test failed: {e}")
        return False

def test_framework_content_generation():
    """Test framework content generation"""
    print_header("Testing Framework Content Generation")
    
    try:
        # Import the improved LLM service
        from backend.services.llm_service_improved import LLMService
        
        # Initialize service with correct config path
        llm_service = LLMService(config_path='config')
        
        # Test framework content generation
        frameworks_content = llm_service._get_frameworks_content()
        
        if not frameworks_content:
            print_error("No framework content generated")
            return False
        
        print_success("Framework content generated successfully")
        print("\nGenerated Framework Content:")
        print("-" * 40)
        print(frameworks_content)
        print("-" * 40)
        
        # Check if content contains expected elements
        expected_elements = [
            "EVALUATION FRAMEWORKS:",
            "PYRAMID PRINCIPLE",
            "SCQA FRAMEWORK", 
            "HEALTHCARE INVESTMENT FRAMEWORK",
            "Description:",
            "Application:"
        ]
        
        for element in expected_elements:
            if element in frameworks_content:
                print_success(f"Found expected element: {element}")
            else:
                print_error(f"Missing expected element: {element}")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Framework content generation test failed: {e}")
        return False

def test_application_guidance_generation():
    """Test application guidance generation"""
    print_header("Testing Application Guidance Generation")
    
    try:
        # Import the improved LLM service
        from backend.services.llm_service_improved import LLMService
        
        # Initialize service with correct config path
        llm_service = LLMService(config_path='config')
        
        # Test application guidance generation
        guidance = llm_service._get_framework_application_guidance()
        
        if not guidance:
            print_error("No application guidance generated")
            return False
        
        print_success("Application guidance generated successfully")
        print("\nGenerated Application Guidance:")
        print("-" * 40)
        print(guidance)
        print("-" * 40)
        
        # Check if guidance contains expected elements
        expected_elements = [
            "Apply",
            "frameworks",
            "evaluation",
            "patient outcomes",
            "compliance",
            "operational efficiency"
        ]
        
        for element in expected_elements:
            if element.lower() in guidance.lower():
                print_success(f"Found expected element: {element}")
            else:
                print_error(f"Missing expected element: {element}")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Application guidance generation test failed: {e}")
        return False

def test_prompt_generation():
    """Test complete prompt generation"""
    print_header("Testing Complete Prompt Generation")
    
    try:
        # Import the improved LLM service
        from backend.services.llm_service_improved import LLMService
        
        # Initialize service with correct config path
        llm_service = LLMService(config_path='config')
        
        # Test prompt generation
        test_text = "This is a test memo for healthcare investment evaluation."
        system_message, user_message = llm_service._generate_prompt(test_text)
        
        if not system_message or not user_message:
            print_error("No prompt generated")
            return False
        
        print_success("Prompt generated successfully")
        
        # Check if the prompt contains the improved framework content
        expected_framework_elements = [
            "PYRAMID PRINCIPLE",
            "SCQA FRAMEWORK",
            "HEALTHCARE INVESTMENT FRAMEWORK",
            "Description:",
            "Application:"
        ]
        
        for element in expected_framework_elements:
            if element in user_message:
                print_success(f"Found framework element in prompt: {element}")
            else:
                print_error(f"Missing framework element in prompt: {element}")
                return False
        
        # Check that old hardcoded content is NOT present
        old_content = [
            "Business Communication Framework",
            "Healthcare Investment Analysis",
            "Strategic Planning Framework"
        ]
        
        for old_element in old_content:
            if old_element in user_message:
                print_error(f"Found old hardcoded content: {old_element}")
                return False
            else:
                print_success(f"Old content properly replaced: {old_element}")
        
        return True
        
    except Exception as e:
        print_error(f"Prompt generation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print_header("Framework Injection Implementation Test (Fixed)")
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Framework Extraction", test_framework_extraction),
        ("Application Guidance", test_application_guidance),
        ("Framework Content Generation", test_framework_content_generation),
        ("Application Guidance Generation", test_application_guidance_generation),
        ("Complete Prompt Generation", test_prompt_generation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"⚠️  {test_name} test failed")
        except Exception as e:
            print_error(f"{test_name} test failed with exception: {e}")
    
    print_header("Test Results Summary")
    print(f"📊 Tests passed: {passed}/{total}")
    print(f"📈 Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print_success("🎉 All tests passed! Framework injection is working correctly.")
        print("\n📋 Implementation Summary:")
        print("✅ Framework definitions extracted from rubric.yaml")
        print("✅ Application guidance extracted from rubric.yaml")
        print("✅ Dynamic framework content generation working")
        print("✅ Dynamic application guidance generation working")
        print("✅ Complete prompt generation with improved frameworks")
        print("✅ Old hardcoded content properly replaced")
        print("\n🔍 Next Steps:")
        print("1. Replace the original llm_service.py with the improved version")
        print("2. Test the evaluation endpoint with the new framework injection")
        print("3. Verify that LLM evaluations use the healthcare-specific frameworks")
        return 0
    else:
        print_error(f"❌ {total - passed} test(s) failed. Framework injection needs fixes.")
        return 1

if __name__ == "__main__":
    exit(main())
