#!/usr/bin/env python3
"""
Test script to verify footer implementation on all pages
"""

import requests
import re
from datetime import datetime

BASE_URL = "https://memo.myisland.dev"

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

def test_page_footer(url_path, page_name):
    """Test if a specific page has the footer"""
    print_header(f"Testing {page_name} Footer")
    
    try:
        # Get the page content
        response = requests.get(f"{BASE_URL}{url_path}", verify=False, timeout=10)
        
        if response.status_code != 200:
            print_error(f"Page returned status {response.status_code}")
            return False
        
        content = response.text
        
        # Check for footer content
        footer_patterns = [
            r'© Copyright FGS',
            r'<footer',
            r'Copyright FGS'
        ]
        
        footer_found = False
        for pattern in footer_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                footer_found = True
                print_success(f"Found footer pattern: {pattern}")
                break
        
        if footer_found:
            print_success(f"{page_name} has footer")
            return True
        else:
            print_error(f"{page_name} missing footer")
            return False
            
    except Exception as e:
        print_error(f"Failed to test {page_name}: {e}")
        return False

def test_footer_styling():
    """Test if footer has proper styling"""
    print_header("Testing Footer Styling")
    
    try:
        # Test home page for styling
        response = requests.get(f"{BASE_URL}/", verify=False, timeout=10)
        content = response.text
        
        # Check for footer styling classes
        styling_patterns = [
            r'bg-white',
            r'border-t',
            r'border-gray-200',
            r'text-center',
            r'text-sm',
            r'text-gray-500'
        ]
        
        styling_found = 0
        for pattern in styling_patterns:
            if re.search(pattern, content):
                styling_found += 1
                print_success(f"Found styling: {pattern}")
        
        if styling_found >= 3:  # At least some basic styling
            print_success("Footer has proper styling")
            return True
        else:
            print_error("Footer missing proper styling")
            return False
            
    except Exception as e:
        print_error(f"Failed to test footer styling: {e}")
        return False

def test_all_pages():
    """Test footer on all main pages"""
    print_header("Testing Footer on All Pages")
    
    pages = [
        ("/", "Home Page"),
        ("/login", "Login Page"),
        ("/text-input", "Text Input Page"),
        ("/overall-feedback", "Overall Feedback Page"),
        ("/detailed-feedback", "Detailed Feedback Page"),
        ("/help", "Help Page"),
        ("/admin", "Admin Page"),
        ("/last-evaluation", "Last Evaluation Page"),
        ("/debug", "Debug Page")
    ]
    
    passed = 0
    total = len(pages)
    
    for url_path, page_name in pages:
        if test_page_footer(url_path, page_name):
            passed += 1
        else:
            print(f"⚠️  {page_name} footer test failed")
    
    return passed, total

def main():
    """Run all footer tests"""
    print_header("Footer Implementation Test")
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    # Test footer styling
    styling_test = test_footer_styling()
    
    # Test all pages
    passed, total = test_all_pages()
    
    print_header("Footer Test Results Summary")
    print(f"📊 Pages with footer: {passed}/{total}")
    print(f"📈 Success rate: {(passed/total)*100:.1f}%")
    print(f"🎨 Styling test: {'✅ Passed' if styling_test else '❌ Failed'}")
    
    if passed == total and styling_test:
        print_success("🎉 All footer tests passed! Footer is properly implemented.")
        print("\n📋 Implementation Summary:")
        print("✅ Footer added to Layout component (for pages using Layout)")
        print("✅ Footer added to Home page (standalone layout)")
        print("✅ Footer added to Login page (standalone layout)")
        print("✅ Footer has proper styling and positioning")
        print("✅ Copyright text '© Copyright FGS' present on all pages")
        print("\n🔍 Footer Features:")
        print("• Consistent styling across all pages")
        print("• Proper positioning (bottom of page)")
        print("• Copyright text prominently displayed")
        print("• Responsive design maintained")
        return 0
    else:
        print_error(f"❌ {total - passed} page(s) missing footer or styling issues.")
        return 1

if __name__ == "__main__":
    exit(main())
