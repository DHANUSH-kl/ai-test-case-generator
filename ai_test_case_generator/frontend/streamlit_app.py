import streamlit as st
import requests
from docx import Document
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Test Case Generator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Backend URL (make configurable if you want)
BACKEND_URL = "https://huggingface.co/spaces/dhanush1023/testCaseGenerator"

def check_backend_health():
    """Check if backend is healthy"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except Exception as e:
        return False, str(e)

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file with error handling"""
    try:
        if uploaded_file.name.endswith(".txt"):
            return uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".docx"):
            doc = Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            return text
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def generate_test_cases_api(srs_text):
    """Call API to generate test cases with better error handling"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/generate_test_cases",
            json={"srs": srs_text},
            timeout=120,  # 2 minute timeout for generation
            headers={"Content-Type": "application/json"}
        )
        
        return response.status_code, response.json()
        
    except requests.exceptions.Timeout:
        return 408, {"error": "Request timed out. Please try with shorter SRS content."}
    except requests.exceptions.ConnectionError:
        return 503, {"error": "Cannot connect to backend service. Please try again later."}
    except requests.exceptions.RequestException as e:
        return 500, {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return 500, {"error": f"Unexpected error: {str(e)}"}

# Main UI
st.markdown('<h1 class="main-header">🧪 AI Test Case Generator</h1>', unsafe_allow_html=True)
st.markdown("Upload your **SRS document** to generate comprehensive test cases using AI.")

# Sidebar for system status and info
with st.sidebar:
    st.header("📊 System Status")
    
    # Check backend health
    if st.button("🔄 Check Backend Status"):
        with st.spinner("Checking backend..."):
            is_healthy, health_data = check_backend_health()
            
            if is_healthy:
                st.markdown(f"""
                <div class="status-box success-box">
                    <strong>✅ Backend Online</strong><br>
                    Memory: {health_data.get('memory', 'N/A')}<br>
                    Model: {health_data.get('model_loaded', 'Unknown')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="status-box error-box">
                    <strong>❌ Backend Offline</strong><br>
                    Error: {health_data or 'Connection failed'}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.header("ℹ️ Instructions")
    st.markdown("""
    1. **Upload** your SRS document (.txt or .docx)
    2. **Review** the extracted content
    3. **Click** Generate Test Cases
    4. **Download** or copy the results
    
    **Supported formats:**
    - Plain text (.txt)
    - Word documents (.docx)
    
    **Tips:**
    - Keep SRS content under 5000 characters
    - Include clear requirements
    - Specify functional details
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload SRS Document")
    uploaded_file = st.file_uploader(
        "Choose your SRS file", 
        type=["txt", "docx"],
        help="Upload a .txt or .docx file containing your Software Requirements Specification"
    )
    
    srs_text = ""
    
    if uploaded_file:
        # Show file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.1f} KB",
            "File type": uploaded_file.type
        }
        
        st.markdown("**📄 File Information:**")
        for key, value in file_details.items():
            st.write(f"- **{key}:** {value}")
        
        # Extract text
        with st.spinner("Extracting text from file..."):
            srs_text = extract_text_from_file(uploaded_file)
        
        if srs_text:
            # Show character count and warnings
            char_count = len(srs_text)
            word_count = len(srs_text.split())
            
            st.markdown(f"**📊 Content Statistics:**")
            st.write(f"- **Characters:** {char_count:,}")
            st.write(f"- **Words:** {word_count:,}")
            
            if char_count > 5000:
                st.warning(f"⚠️ Content is {char_count:,} characters. It will be truncated to 5000 characters for processing.")
            elif char_count < 100:
                st.warning("⚠️ Content seems very short. Consider adding more detailed requirements for better test cases.")
        else:
            st.error("❌ Failed to extract text from the uploaded file.")

with col2:
    if srs_text:
        st.subheader("📄 Extracted SRS Content")
        
        # Show preview of content
        preview_text = srs_text[:1000] + "..." if len(srs_text) > 1000 else srs_text
        st.text_area(
            "SRS Content Preview", 
            preview_text, 
            height=300,
            help="This shows the first 1000 characters of your extracted content"
        )
        
        # Show full content in expander
        with st.expander("👁️ View Full Content"):
            st.text(srs_text)

# Generation section
if srs_text:
    st.markdown("---")
    st.subheader("🚀 Generate Test Cases")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🧪 Generate Test Cases", type="primary", use_container_width=True):
            
            # Validate empty input (extra safety)
            if not srs_text.strip():
                st.error("❌ SRS content is empty. Please upload a valid SRS document.")
            else:
                # Show generation progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔄 Connecting to AI backend...")
                progress_bar.progress(20)
                time.sleep(0.5)
                
                status_text.text("🤖 AI is analyzing your SRS...")
                progress_bar.progress(40)
                
                # Call API
                start_time = time.time()
                status_code, response_data = generate_test_cases_api(srs_text)
                generation_time = time.time() - start_time
                
                progress_bar.progress(80)
                status_text.text("✨ Formatting test cases...")
                time.sleep(0.5)
                
                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
                
                # Handle response
                if status_code == 200:
                    test_cases = response_data.get("test_cases", [])
                    
                    model_used = response_data.get("model_used", "AI Model")
                    generation_method = response_data.get("generation_method", "Primary AI Model")
                    fallback_used = response_data.get("fallback_to_template", False)
                    
                    if test_cases:
                        st.markdown(f"""
                        <div class="status-box success-box">
                            <strong>✅ Successfully Generated {len(test_cases)} Test Cases</strong><br>
                            Generation time: {generation_time:.1f}s<br>
                            Model used: {model_used}<br>
                            Generation method: {generation_method}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if fallback_used:
                            st.info("ℹ️ The AI model fell back to template-based generation for this output to ensure stability.")
                        
                        st.subheader("📋 Generated Test Cases")
                        
                        # Display test cases with better formatting
                        for i, tc in enumerate(test_cases, 1):
                            with st.expander(f"**Test Case {i:02d}**", expanded=True):
                                # Parse test case components
                                if ' - ' in tc:
                                    parts = tc.split(' - ')
                                    if len(parts) >= 3:
                                        tc_id_objective = parts[0]
                                        steps = parts[1]
                                        expected = ' - '.join(parts[2:])
                                        
                                        st.markdown(f"**🎯 Objective:** {tc_id_objective}")
                                        st.markdown(f"**📝 Steps:** {steps}")
                                        st.markdown(f"**✅ Expected Result:** {expected}")
                                    else:
                                        st.write(tc)
                                else:
                                    st.write(tc)
                        
                        # Export options
                        st.markdown("---")
                        st.subheader("💾 Export Options")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Text export
                            export_text = "\n".join([f"{i}. {tc}" for i, tc in enumerate(test_cases, 1)])
                            st.download_button(
                                label="📄 Download as Text",
                                data=export_text,
                                file_name=f"test_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                        
                        with col2:
                            # Copy to clipboard option
                            if st.button("📋 Copy to Clipboard"):
                                st.code(export_text, language=None)
                                st.success("✅ Test cases displayed above for copying!")
                    
                    else:
                        st.markdown("""
                        <div class="status-box error-box">
                            <strong>❌ No test cases generated</strong><br>
                            The AI couldn't generate test cases from your SRS content.
                        </div>
                        """, unsafe_allow_html=True)
                        
                else:
                    error_msg = response_data.get("error", "Unknown error occurred")
                    st.markdown(f"""
                    <div class="status-box error-box">
                        <strong>❌ Generation Failed</strong><br>
                        Error: {error_msg}<br>
                        Status Code: {status_code}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Provide helpful suggestions
                    if status_code == 408:
                        st.info("💡 **Tip:** Try with shorter SRS content or simpler requirements.")
                    elif status_code == 503:
                        st.info("💡 **Tip:** Backend service might be starting up. Please wait a moment and try again.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🧪 AI Test Case Generator | Powered by Advanced Language Models</p>
    <p><small>Upload your SRS documents and get comprehensive test cases in seconds!</small></p>
</div>
""", unsafe_allow_html=True)
