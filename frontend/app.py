"""
Memo AI Coach - Frontend Application
Streamlit-based user interface for text evaluation
"""

import streamlit as st
import requests
import yaml
import os
from typing import Dict, Any

# Page configuration
st.set_page_config(
    page_title="Memo AI Coach",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'evaluation_results' not in st.session_state:
    st.session_state.evaluation_results = None
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Text Input"

def get_backend_url():
    """Get backend URL from environment or default"""
    return os.getenv('BACKEND_URL', 'http://localhost:8000')

def create_session():
    """Create a new session with the backend"""
    try:
        response = requests.get(f"{get_backend_url()}/api/v1/sessions/create")
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('session_id')
    except Exception as e:
        st.error(f"Failed to create session: {e}")
    return None

def submit_text_for_evaluation(text_content: str) -> Dict[str, Any]:
    """Submit text for evaluation"""
    if not st.session_state.session_id:
        st.session_state.session_id = create_session()
    
    if not st.session_state.session_id:
        st.error("Failed to create session")
        return None
    
    try:
        response = requests.post(
            f"{get_backend_url()}/api/v1/evaluations/submit",
            json={
                "text_content": text_content,
                "session_id": st.session_state.session_id
            },
            headers={"X-Session-ID": st.session_state.session_id}
        )
        
        if response.status_code == 200:
            return response.json().get('data', {})
        else:
            st.error(f"Evaluation failed: {response.json().get('errors', [])}")
            return None
    except Exception as e:
        st.error(f"Failed to submit text: {e}")
        return None

def main():
    """Main application function"""
    st.title("📝 Memo AI Coach")
    st.markdown("Intelligent text evaluation and feedback system")
    
    # Create tabs
    tabs = st.tabs([
        "Text Input", 
        "Overall Feedback", 
        "Detailed Feedback", 
        "Help", 
        "Admin"
    ])
    
    # Text Input Tab
    with tabs[0]:
        st.header("Submit Text for Evaluation")
        st.markdown("Enter your text below for comprehensive AI-powered evaluation and feedback.")
        
        # Text input area
        text_content = st.text_area(
            "Text to Evaluate",
            height=300,
            placeholder="Enter your text here (maximum 10,000 characters)...",
            help="Enter the text you want to be evaluated. The system will provide comprehensive feedback including strengths, areas for improvement, and detailed scoring."
        )
        
        # Character counter
        if text_content:
            char_count = len(text_content)
            st.write(f"Character count: {char_count}/10,000")
            
            if char_count > 10000:
                st.error("Text exceeds maximum length of 10,000 characters")
                return
        
        # Submit button
        if st.button("Submit for Evaluation", type="primary"):
            if not text_content or len(text_content.strip()) == 0:
                st.error("Please enter some text for evaluation")
                return
            
            with st.spinner("Evaluating your text..."):
                results = submit_text_for_evaluation(text_content)
                if results:
                    st.session_state.evaluation_results = results
                    st.success("Evaluation completed successfully!")
                    st.rerun()
    
    # Overall Feedback Tab
    with tabs[1]:
        st.header("Overall Feedback")
        
        if st.session_state.evaluation_results:
            results = st.session_state.evaluation_results.get('evaluation', {})
            
            # Overall score
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                score = results.get('overall_score', 0)
                st.metric("Overall Score", f"{score:.1f}/5.0")
            
            # Strengths and opportunities
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Strengths")
                strengths = results.get('strengths', '')
                if strengths:
                    st.write(strengths)
                else:
                    st.info("No strengths identified")
            
            with col2:
                st.subheader("Opportunities for Improvement")
                opportunities = results.get('opportunities', '')
                if opportunities:
                    st.write(opportunities)
                else:
                    st.info("No improvement opportunities identified")
            
            # Rubric scores
            st.subheader("Detailed Rubric Scores")
            rubric_scores = results.get('rubric_scores', {})
            if rubric_scores:
                for category, score in rubric_scores.items():
                    st.metric(category.replace('_', ' ').title(), f"{score}/5")
        else:
            st.info("Submit text for evaluation to see overall feedback")
    
    # Detailed Feedback Tab
    with tabs[2]:
        st.header("Detailed Feedback")
        
        if st.session_state.evaluation_results:
            results = st.session_state.evaluation_results.get('evaluation', {})
            segment_feedback = results.get('segment_feedback', [])
            
            if segment_feedback:
                for i, segment in enumerate(segment_feedback):
                    with st.expander(f"Segment {i+1}: {segment.get('segment', '')[:50]}..."):
                        st.write("**Original Text:**")
                        st.write(segment.get('segment', ''))
                        
                        st.write("**Feedback:**")
                        st.write(segment.get('comment', ''))
                        
                        questions = segment.get('questions', [])
                        if questions:
                            st.write("**Questions for Reflection:**")
                            for j, question in enumerate(questions, 1):
                                st.write(f"{j}. {question}")
            else:
                st.info("No segment-level feedback available")
        else:
            st.info("Submit text for evaluation to see detailed feedback")
    
    # Help Tab
    with tabs[3]:
        st.header("Help & Resources")
        
        st.subheader("How to Use Memo AI Coach")
        st.markdown("""
        1. **Submit Text**: Go to the Text Input tab and enter your text for evaluation
        2. **Review Feedback**: Check the Overall Feedback tab for comprehensive analysis
        3. **Detailed Analysis**: Visit the Detailed Feedback tab for segment-level insights
        4. **Admin Functions**: Access configuration and system management (admin only)
        """)
        
        st.subheader("Evaluation Framework")
        st.markdown("""
        The system evaluates your text based on four key criteria:
        - **Overall Structure**: Organization and logical flow
        - **Content Quality**: Depth and relevance of content
        - **Clarity & Communication**: Effectiveness of expression
        - **Technical Accuracy**: Factual correctness and precision
        """)
        
        st.subheader("Scoring System")
        st.markdown("""
        Each criterion is scored on a scale of 1-5:
        - **5**: Exceptional quality
        - **4**: Good quality
        - **3**: Adequate quality
        - **2**: Poor quality
        - **1**: Very poor quality
        """)
    
    # Admin Tab
    with tabs[4]:
        st.header("Admin Panel")
        
        # Simple admin authentication
        admin_username = st.text_input("Admin Username")
        admin_password = st.text_input("Admin Password", type="password")
        
        if st.button("Login"):
            if admin_username == "admin" and admin_password == os.getenv("ADMIN_PASSWORD", ""):
                st.success("Admin access granted")
                st.session_state.admin_authenticated = True
            else:
                st.error("Invalid credentials")
        
        if st.session_state.get('admin_authenticated'):
            st.subheader("Configuration Management")
            st.info("Configuration management features will be implemented here")
            
            st.subheader("System Status")
            try:
                response = requests.get(f"{get_backend_url()}/health")
                if response.status_code == 200:
                    st.success("Backend service is healthy")
                else:
                    st.error("Backend service is unhealthy")
            except Exception as e:
                st.error(f"Backend service is unreachable: {e}")

if __name__ == "__main__":
    main()
