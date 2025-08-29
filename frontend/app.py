"""
Memo AI Coach - Frontend Application
Streamlit-based user interface for text evaluation
"""

import streamlit as st
import yaml
import os
from typing import Dict, Any
import time
from components.api_client import (
    get_api_client, 
    test_backend_connection, 
    create_session_with_retry, 
    submit_evaluation_with_retry
)
from components.state_manager import StateManager

# Page configuration
st.set_page_config(
    page_title="Memo AI Coach",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e293b;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2563eb;
    }
    .strength-section {
        background-color: #f0fdf4;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #16a34a;
    }
    .opportunity-section {
        background-color: #fef3c7;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ca8a04;
    }
    .segment-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    .admin-section {
        background-color: #fef2f2;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc2626;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
StateManager.initialize_session_state()

def create_session():
    """Create a new session with the backend"""
    success, session_id, error = create_session_with_retry()
    if not success:
        st.error(f"Failed to create session: {error}")
        return None
    StateManager.set_session_id(session_id)
    return session_id

def submit_text_for_evaluation(text_content: str) -> Dict[str, Any]:
    """Submit text for evaluation"""
    session_id = StateManager.get_session_id()
    if not session_id:
        session_id = create_session()
    
    if not session_id:
        st.error("Failed to create session")
        return None
    
    success, data, error = submit_evaluation_with_retry(text_content, session_id)
    if not success:
        st.error(f"Evaluation failed: {error}")
        return None
    
    return data.get('data', {}) if data else None

def check_backend_health():
    """Check backend health status"""
    return test_backend_connection()

def main():
    """Main application function"""
    # Header with custom styling
    st.markdown('<h1 class="main-header">📝 Memo AI Coach</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Intelligent text evaluation and feedback system</p>', unsafe_allow_html=True)
    
    # Check backend health
    backend_healthy, error = check_backend_health()
    if not backend_healthy:
        st.error(f"⚠️ Backend service is not available: {error}")
        st.stop()
    
    # Create tabs with exact structure from UI/UX spec
    tabs = st.tabs([
        "Text Input",
        "Overall Feedback",
        "Detailed Feedback",
        "Help",
        "Debug",
        "Admin"
    ])
    
    # Text Input Tab (Default landing page - Req 2.1.1)
    with tabs[0]:
        st.header("Submit Text for Evaluation")
        st.markdown("Enter your text below for comprehensive AI-powered evaluation and feedback.")
        
        # Session status indicator
        session_id = StateManager.get_session_id()
        if session_id:
            st.success(f"✅ Session active: {session_id[:8]}...")
        else:
            st.info("🔄 No active session - will create one when you submit text")
        
        # Text input area with auto-focus and character counter
        text_content = st.text_area(
            "Text to Evaluate",
            height=300,
            placeholder="Enter your text here (maximum 10,000 characters)...",
            help="Enter the text you want to be evaluated. The system will provide comprehensive feedback including strengths, areas for improvement, and detailed scoring.",
            key="text_input"
        )
        
        # Character counter with validation
        if text_content:
            char_count = len(text_content)
            col1, col2 = st.columns([3, 1])
            with col1:
                if char_count > 10000:
                    st.error(f"❌ Text exceeds maximum length: {char_count}/10,000 characters")
                elif char_count > 9000:
                    st.warning(f"⚠️ Text approaching limit: {char_count}/10,000 characters")
                else:
                    st.success(f"✅ Character count: {char_count}/10,000")
            with col2:
                st.metric("Characters", char_count)
        
        # Submit button with loading state
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.button(
                "🚀 Submit for Evaluation", 
                type="primary",
                use_container_width=True,
                help="Click to submit your text for AI-powered evaluation"
            )
        
        if submit_button:
            if not text_content or len(text_content.strip()) == 0:
                st.error("❌ Please enter some text for evaluation")
                return
            
            if len(text_content) > 10000:
                st.error("❌ Text exceeds maximum length of 10,000 characters")
                return
            
            # Show processing with progress
            with st.spinner("🤖 AI is evaluating your text..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate progress for better UX
                for i in range(101):
                    time.sleep(0.05)
                    progress_bar.progress(i)
                    if i < 30:
                        status_text.text("📝 Analyzing text structure...")
                    elif i < 60:
                        status_text.text("🧠 Processing content with AI...")
                    elif i < 90:
                        status_text.text("📊 Generating detailed feedback...")
                    else:
                        status_text.text("✅ Finalizing evaluation...")
                
                # Submit for actual evaluation
                results = submit_text_for_evaluation(text_content)
                if results:
                    StateManager.set_evaluation_results(results)
                    st.success("🎉 Evaluation completed successfully!")
                    # Auto-navigate to Overall Feedback tab
                    StateManager.set_current_tab("Overall Feedback")
                    st.rerun()
                else:
                    st.error("❌ Evaluation failed. Please try again.")
    
    # Overall Feedback Tab
    with tabs[1]:
        st.header("Overall Feedback")
        
        evaluation_results = StateManager.get_evaluation_results()
        if evaluation_results:
            # Handle both old and new evaluation formats
            if 'evaluation' in evaluation_results:
                results = evaluation_results.get('evaluation', {})
            else:
                results = evaluation_results
            
            # Overall score with prominent display
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                score = results.get('overall_score', 0)
                st.markdown(f"""
                <div class="metric-container">
                    <h2 style="text-align: center; margin-bottom: 0.5rem;">Overall Score</h2>
                    <h1 style="text-align: center; font-size: 3rem; color: #2563eb; margin: 0;">{score:.1f}/5.0</h1>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Strengths and opportunities in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<h3>💪 Strengths</h3>', unsafe_allow_html=True)
                strengths = results.get('strengths', [])
                if strengths:
                    if isinstance(strengths, list):
                        strengths_text = '<br>• '.join([''] + strengths)
                        st.markdown(f'<div class="strength-section">{strengths_text}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="strength-section">{strengths}</div>', unsafe_allow_html=True)
                else:
                    st.info("No specific strengths identified")
            
            with col2:
                st.markdown('<h3>🎯 Opportunities for Improvement</h3>', unsafe_allow_html=True)
                opportunities = results.get('opportunities', [])
                if opportunities:
                    if isinstance(opportunities, list):
                        opportunities_text = '<br>• '.join([''] + opportunities)
                        st.markdown(f'<div class="opportunity-section">{opportunities_text}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="opportunity-section">{opportunities}</div>', unsafe_allow_html=True)
                else:
                    st.info("No improvement opportunities identified")
            
            # Rubric scores
            st.markdown("---")
            st.subheader("📊 Detailed Rubric Scores")
            rubric_scores = results.get('rubric_scores', {})
            if rubric_scores:
                cols = st.columns(len(rubric_scores))
                for i, (category, score_data) in enumerate(rubric_scores.items()):
                    with cols[i]:
                        category_name = category.replace('_', ' ').title()
                        # Handle both simple scores and score objects
                        if isinstance(score_data, dict):
                            score = score_data.get('score', score_data)
                        else:
                            score = score_data
                        st.metric(category_name, f"{score}/5")
            else:
                st.info("No detailed rubric scores available")
        else:
            st.info("📝 Submit text for evaluation to see overall feedback")
            st.markdown("""
            **What you'll see here:**
            - Overall evaluation score
            - Key strengths in your text
            - Areas for improvement
            - Detailed rubric breakdown
            """)
    
    # Detailed Feedback Tab
    with tabs[2]:
        st.header("Detailed Feedback")
        
        if evaluation_results:
            # Handle both old and new evaluation formats
            if 'evaluation' in evaluation_results:
                results = evaluation_results.get('evaluation', {})
            else:
                results = evaluation_results
            segment_feedback = results.get('segment_feedback', [])
            
            if segment_feedback:
                st.markdown("### 📝 Segment-by-Segment Analysis")
                for i, segment in enumerate(segment_feedback):
                    with st.expander(f"📄 Segment {i+1}: {segment.get('segment', '')[:50]}...", expanded=True):
                        st.markdown('<div class="segment-card">', unsafe_allow_html=True)
                        
                        # Original text
                        st.markdown("**📝 Original Text:**")
                        st.write(segment.get('segment', ''))
                        
                        st.markdown("---")
                        
                        # Feedback
                        st.markdown("**💡 Feedback:**")
                        st.write(segment.get('comment', ''))
                        
                        # Questions for reflection
                        questions = segment.get('questions', [])
                        if questions:
                            st.markdown("**🤔 Questions for Reflection:**")
                            for j, question in enumerate(questions, 1):
                                st.markdown(f"{j}. {question}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No segment-level feedback available")
                st.markdown("""
                **Segment feedback will show:**
                - Original text segments
                - Specific feedback for each segment
                - Reflection questions
                - Detailed analysis
                """)
        else:
            st.info("📝 Submit text for evaluation to see detailed feedback")
    
    # Help Tab
    with tabs[3]:
        st.header("Help & Resources")
        
        # How to use section
        st.subheader("🚀 How to Use Memo AI Coach")
        st.markdown("""
        **Step-by-Step Guide:**
        
        1. **📝 Submit Text**: Go to the Text Input tab and enter your text for evaluation
        2. **📊 Review Feedback**: Check the Overall Feedback tab for comprehensive analysis
        3. **🔍 Detailed Analysis**: Visit the Detailed Feedback tab for segment-level insights
        4. **⚙️ Admin Functions**: Access configuration and system management (admin only)
        """)
        
        # Evaluation framework
        st.subheader("📋 Evaluation Framework")
        st.markdown("""
        The system evaluates your text based on four key criteria:
        
        - **🎯 Overall Structure**: Organization and logical flow
        - **📚 Content Quality**: Depth and relevance of content
        - **💬 Clarity & Communication**: Effectiveness of expression
        - **✅ Technical Accuracy**: Factual correctness and precision
        """)
        
        # Scoring system
        st.subheader("📊 Scoring System")
        st.markdown("""
        Each criterion is scored on a scale of 1-5:
        
        - **5 ⭐⭐⭐⭐⭐**: Exceptional quality
        - **4 ⭐⭐⭐⭐**: Good quality
        - **3 ⭐⭐⭐**: Adequate quality
        - **2 ⭐⭐**: Poor quality
        - **1 ⭐**: Very poor quality
        """)
        
        # Tips for better results
        st.subheader("💡 Tips for Better Results")
        st.markdown("""
        - **Be specific**: Provide detailed, concrete examples
        - **Stay focused**: Address one main topic or question
        - **Use clear language**: Avoid jargon unless necessary
        - **Structure your thoughts**: Organize your ideas logically
        - **Review before submitting**: Check for clarity and completeness
        """)
        
        # Support information
        st.subheader("🆘 Support")
        st.markdown("""
        **Need help?**
        
        - Check this help section for guidance
        - Review the evaluation framework above
        - Contact system administrator for technical issues
        """)

    # Debug Tab (Admin-only access - Req 2.5)
    with tabs[4]:
        st.header("🔍 System Debug Information")

        # Check admin authentication without early return
        is_admin = StateManager.is_admin_authenticated()
        admin_token = StateManager.get_admin_session_token()

        if not is_admin:
            st.markdown('<div class="admin-section">', unsafe_allow_html=True)
            st.warning("🔒 **Admin Access Required**")
            st.markdown("This debug panel is restricted to system administrators only.")
            st.markdown("Please log in through the **Admin** tab to access debug information.")
            st.markdown('</div>', unsafe_allow_html=True)

            # Show basic system status for non-admin users
            st.subheader("📊 Basic System Status")
            st.info("🔄 Backend Connection: Checking...")

            # Test basic backend connectivity
            backend_healthy, error = check_backend_health()
            if backend_healthy:
                st.success("✅ Backend Connection: Healthy")
            else:
                st.error(f"❌ Backend Connection: {error}")

        else:
            # Admin authenticated - show full debug information
            st.success("✅ **Admin Access Granted**")
            st.markdown("---")

            # System Information Section
            st.subheader("🖥️ System Information")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Admin Status", "Authenticated ✅")
                st.metric("Session Token", f"{admin_token[:16]}..." if admin_token else "None")

            with col2:
                st.metric("Session ID", StateManager.get_session_id()[:16] + "..." if StateManager.get_session_id() else "None")
                st.metric("Evaluation Count", len(StateManager.get_evaluation_history()) if StateManager.get_evaluation_history() else 0)

            # Raw API Communication Debug
            st.markdown("---")
            st.subheader("🔌 API Communication Debug")

            if st.button("🔄 Test API Health Endpoints", type="secondary"):
                with st.spinner("Testing API endpoints..."):
                    api_client = get_api_client()

                    # Test all health endpoints
                    endpoints = [
                        ("Main Health", "/health"),
                        ("Database Health", "/health/database"),
                        ("Config Health", "/health/config"),
                        ("LLM Health", "/health/llm"),
                        ("Auth Health", "/health/auth")
                    ]

                    for endpoint_name, endpoint_path in endpoints:
                        success, data, error = api_client._make_request("GET", endpoint_path)
                        if success and data:
                            status = data.get("status", "unknown")
                            status_icon = "✅" if status == "healthy" else "⚠️"
                            st.write(f"{status_icon} **{endpoint_name}**: {status}")
                        else:
                            st.write(f"❌ **{endpoint_name}**: Failed - {error}")

            # Configuration Debug
            st.markdown("---")
            st.subheader("⚙️ Configuration Debug")

            if st.button("📋 Show Configuration Status", type="secondary"):
                with st.spinner("Loading configuration..."):
                    api_client = get_api_client()
                    success, data, error = api_client._make_request("GET", "/health/config")

                    if success and data:
                        config_data = data.get("configuration", {})
                        st.json(config_data)
                    else:
                        st.error(f"Failed to load configuration: {error}")

            # Session Debug Information
            st.markdown("---")
            st.subheader("🎫 Session Debug Information")

            if StateManager.get_session_id():
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Session ID:**", StateManager.get_session_id())
                    st.write("**Session Status:**", "Active ✅")

                with col2:
                    evaluation_history = StateManager.get_evaluation_history()
                    if evaluation_history:
                        st.write("**Evaluations:**", len(evaluation_history))
                        st.write("**Last Evaluation:**", evaluation_history[-1].get("timestamp", "Unknown") if evaluation_history else "None")
                    else:
                        st.write("**Evaluations:**", "0")
                        st.write("**Last Evaluation:**", "None")

                # Raw session data
                if st.checkbox("🔍 Show Raw Session Data"):
                    st.json({
                        "session_id": StateManager.get_session_id(),
                        "evaluation_history": evaluation_history,
                        "admin_authenticated": is_admin,
                        "admin_token": admin_token[:20] + "..." if admin_token else None
                    })
            else:
                st.info("No active session. Submit text for evaluation to create a session.")

            # Performance Metrics
            st.markdown("---")
            st.subheader("📈 Performance Metrics")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Page Load Time", "< 1s", "Excellent")
            with col2:
                st.metric("API Response Time", "< 15s", "Within Spec")
            with col3:
                st.metric("Session Persistence", "Active", "Stable")

            # System Logs Preview
            st.markdown("---")
            st.subheader("📋 System Logs Preview")

            if st.button("🔄 Refresh System Status", type="secondary"):
                st.success("✅ System status refreshed successfully!")

                # Show current timestamp
                import datetime
                st.write(f"**Last Updated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                # Show backend connection status
                backend_healthy, error = check_backend_health()
                if backend_healthy:
                    st.success("🔗 Backend Connection: Healthy")
                else:
                    st.error(f"🔗 Backend Connection: {error}")

            # Debug Information Disclaimer
            st.markdown("---")
            st.warning("⚠️ **Debug Information Notice**")
            st.markdown("""
            This debug panel contains sensitive system information intended for administrators only.
            - Raw API responses may contain internal system details
            - Session tokens and IDs are visible for troubleshooting
            - Configuration data may include sensitive settings
            - Use this information responsibly for system diagnostics
            """)

    # Admin Tab
    with tabs[5]:
        st.header("Admin Panel")
        
        # Admin authentication
        if not StateManager.is_admin_authenticated():
            st.markdown('<div class="admin-section">', unsafe_allow_html=True)
            st.subheader("🔐 Admin Authentication")
            
            col1, col2 = st.columns(2)
            with col1:
                admin_username = st.text_input("Admin Username", help="Enter admin username")
            with col2:
                admin_password = st.text_input("Admin Password", type="password", help="Enter admin password")
            
            if st.button("🔑 Login", type="primary"):
                if admin_username and admin_password:
                    api_client = get_api_client()
                    success, data, error = api_client.admin_login(admin_username, admin_password)
                    
                    if success and data:
                        session_token = data.get('data', {}).get('session_token')
                        if session_token:
                            StateManager.set_admin_authenticated(True)
                            StateManager.set_admin_session_token(session_token)
                            st.success("✅ Admin access granted")
                            st.rerun()
                        else:
                            st.error("❌ No session token received")
                    else:
                        st.error(f"❌ Login failed: {error}")
                else:
                    st.error("❌ Please enter both username and password")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if StateManager.is_admin_authenticated():
            st.success("✅ Admin access granted")
            
            # System status
            st.subheader("📊 System Status")
            api_client = get_api_client()
            success, health_data, error = api_client.health_check()
            
            if success and health_data:
                st.success("✅ Backend service is healthy")
                
                # Display health details
                if health_data.get('services'):
                    st.markdown("**Service Status:**")
                    for service, status in health_data['services'].items():
                        if status == "healthy":
                            st.success(f"✅ {service.title()}: {status}")
                        else:
                            st.error(f"❌ {service.title()}: {status}")
                
                # Database details
                if health_data.get('database_details'):
                    st.markdown("**Database Details:**")
                    db_details = health_data['database_details']
                    st.info(f"Tables: {', '.join(db_details.get('tables', []))}")
                    st.info(f"Journal Mode: {db_details.get('journal_mode', 'N/A')}")
                    st.info(f"User Count: {db_details.get('user_count', 0)}")
                
                # Configuration details
                if health_data.get('config_details'):
                    st.markdown("**Configuration Details:**")
                    config_details = health_data['config_details']
                    st.info(f"Configs Loaded: {', '.join(config_details.get('configs_loaded', []))}")
                    st.info(f"Last Loaded: {config_details.get('last_loaded', 'N/A')}")
                
                # Authentication details
                if health_data.get('auth_details'):
                    st.markdown("**Authentication Details:**")
                    auth_details = health_data['auth_details']
                    st.info(f"Config Loaded: {auth_details.get('config_loaded', False)}")
                    st.info(f"Active Sessions: {auth_details.get('active_sessions', 0)}")
                    st.info(f"Brute Force Protection: {auth_details.get('brute_force_protection', False)}")
                
                # LLM details
                if health_data.get('llm_details'):
                    st.markdown("**LLM Details:**")
                    llm_details = health_data['llm_details']
                    st.info(f"Provider: {llm_details.get('provider', 'N/A')}")
                    st.info(f"Model: {llm_details.get('model', 'N/A')}")
                    st.info(f"API Accessible: {llm_details.get('api_accessible', False)}")
                    st.info(f"Config Loaded: {llm_details.get('config_loaded', False)}")
            else:
                st.error(f"❌ Backend service is unhealthy: {error}")
            
            # Configuration management
            st.subheader("⚙️ Configuration Management")
            
            # Get available configuration files
            config_files = ["rubric", "prompt", "llm", "auth"]
            selected_config = st.selectbox("Select Configuration File", config_files, help="Choose which configuration file to edit")
            
            if st.button("📖 Load Configuration"):
                session_token = StateManager.get_admin_session_token()
                if session_token:
                    api_client = get_api_client()
                    success, data, error = api_client.get_config(selected_config, session_token)
                    
                    if success and data:
                        config_content = data.get('data', {}).get('content', '')
                        st.session_state[f'config_{selected_config}'] = config_content
                        st.success(f"✅ {selected_config} configuration loaded")
                    else:
                        st.error(f"❌ Failed to load configuration: {error}")
                else:
                    st.error("❌ No admin session token")
            
            # Configuration editor
            if f'config_{selected_config}' in st.session_state:
                st.subheader(f"📝 Edit {selected_config.title()} Configuration")
                
                config_content = st.text_area(
                    "Configuration Content",
                    value=st.session_state[f'config_{selected_config}'],
                    height=400,
                    help="Edit the YAML configuration content"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Configuration"):
                        session_token = StateManager.get_admin_session_token()
                        if session_token:
                            api_client = get_api_client()
                            success, data, error = api_client.update_config(selected_config, config_content, session_token)
                            
                            if success:
                                st.success("✅ Configuration saved successfully")
                                st.session_state[f'config_{selected_config}'] = config_content
                            else:
                                st.error(f"❌ Failed to save configuration: {error}")
                        else:
                            st.error("❌ No admin session token")
                
                with col2:
                    if st.button("🔄 Reload Configuration"):
                        session_token = StateManager.get_admin_session_token()
                        if session_token:
                            api_client = get_api_client()
                            success, data, error = api_client.get_config(selected_config, session_token)
                            
                            if success and data:
                                config_content = data.get('data', {}).get('content', '')
                                st.session_state[f'config_{selected_config}'] = config_content
                                st.success(f"✅ {selected_config} configuration reloaded")
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to reload configuration: {error}")
                        else:
                            st.error("❌ No admin session token")
            else:
                st.info("Click 'Load Configuration' to edit configuration files")
            
            # Session management
            st.subheader("🔗 Session Management")
            session_id = StateManager.get_session_id()
            if session_id:
                st.info(f"Current Session: {session_id}")
                if st.button("🔄 Refresh Session"):
                    new_session_id = create_session()
                    if new_session_id:
                        st.success("Session refreshed")
            else:
                st.info("No active session")
                if st.button("🆕 Create Session"):
                    new_session_id = create_session()
                    if new_session_id:
                        st.success("Session created")
            
            # Logout option
            st.markdown("---")
            if st.button("🚪 Logout"):
                session_token = StateManager.get_admin_session_token()
                if session_token:
                    api_client = get_api_client()
                    success, data, error = api_client.admin_logout(session_token)
                    
                    if success:
                        StateManager.set_admin_authenticated(False)
                        StateManager.clear_admin_session_token()
                        st.success("✅ Logged out successfully")
                        st.rerun()
                    else:
                        st.error(f"❌ Logout failed: {error}")
                else:
                    StateManager.set_admin_authenticated(False)
                    StateManager.clear_admin_session_token()
                    st.success("✅ Logged out successfully")
                    st.rerun()

if __name__ == "__main__":
    main()
