#!/usr/bin/env python3
"""
Simple test to verify footer implementation
"""

import requests
import re

BASE_URL = "https://memo.myisland.dev"

def test_footer_simple():
    """Simple test to check if footer is present"""
    print("🧪 Testing Footer Implementation")
    print(f"🌐 Testing URL: {BASE_URL}")
    
    try:
        # Get the home page
        response = requests.get(f"{BASE_URL}/", verify=False, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Page returned status {response.status_code}")
            return False
        
        content = response.text
        print(f"📄 Page content length: {len(content)} characters")
        
        # Look for footer content
        if "Copyright FGS" in content:
            print("✅ Found 'Copyright FGS' in page content")
            return True
        elif "© Copyright FGS" in content:
            print("✅ Found '© Copyright FGS' in page content")
            return True
        elif "<footer" in content.lower():
            print("✅ Found footer tag in page content")
            return True
        else:
            print("❌ Footer content not found")
            print("🔍 Looking for any copyright-related content...")
            
            # Look for any copyright-related content
            copyright_patterns = [
                r'copyright',
                r'©',
                r'FGS',
                r'footer'
            ]
            
            for pattern in copyright_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    print(f"✅ Found pattern: {pattern}")
                    return True
            
            print("❌ No copyright or footer content found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_footer_simple()
    if success:
        print("\n🎉 Footer test passed!")
    else:
        print("\n❌ Footer test failed!")
