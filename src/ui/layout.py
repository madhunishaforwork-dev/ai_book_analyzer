import streamlit as st
import time
from datetime import datetime
from src.config import *
from src.ui.styles import get_custom_css
from src.core.processor import extract_text_from_pdf, chunk_documents
from src.core.analyzer import AnalysisEngine
from src.core.analytics import AnalyticsEngine
from src.utils.exporters import create_txt_report, create_json_report, create_html_report

def render_sidebar():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("📚 Intelligent Reader")
        
        # User Info
        user = st.session_state.get('user', {})
        role = user.get('role', 'Guest')
        st.info(f"👤 {user.get('email', 'Guest User')}\n\nKey: 🔑 {role}")
        
        if st.button("Log Out"):
            st.session_state.clear()
            st.rerun()
            
        st.markdown("---")
        
        # Settings
        chunk_size = st.slider("Chunk Size (Tokens)", 500, 3000, 1000, 
                             help="Smaller chunks = more details. Larger chunks = better context.")
        
        sensitivity = st.select_slider("Analysis Depth", options=["Brief", "Standard", "Deep"], value="Standard")
        
        st.markdown("---")
        
        # API Key
        default_key = st.secrets.get("GEMINI_API_KEY", "") if "GEMINI_API_KEY" in st.secrets else ""
        api_key = st.text_input("Gemini API Key (Optional)", value=default_key, type="password", help="Providing an API key unlocks Generative Summaries and Chat.")
        
        user_goal = st.selectbox(
            "🎯 Reading Purpose",
            options=["General Reading", "Exam Preparation", "Research / Academic", "Quick Revision"],
            index=0,
            help="Adapts the AI's explanation style and focus."
        )
        
        st.markdown("---")
        st.markdown("### 📊 Features")
        st.success("✅ Smart PDF Parsing")
        st.success("✅ Statistical NLP")
        st.success("✅ Generative AI (with Key)")
        
        st.markdown("---")
        st.markdown("### 🔒 Privacy")
        if st.button("🗑️ Clear My History"):
            if 'analyzer' in st.session_state and st.session_state.analyzer:
                msg = st.session_state.analyzer.context_manager.clear_history()
                st.success(msg)
            else:
                st.info("No active history to clear.")
        

        with st.expander("👤 View Profile Data"):
            if 'analyzer' in st.session_state and st.session_state.analyzer:
                ctx = st.session_state.analyzer.context_manager.context
                
                st.caption(f"**User ID:** `{ctx.get('user_id', 'Unknown')}`")
                st.caption(f"**Last Active:** {datetime.fromtimestamp(ctx.get('last_active', time.time())).strftime('%Y-%m-%d %H:%M')}")
                
                st.markdown("#### 🧠 Preferences")
                prefs = ctx.get('preferences', {})
                st.write(f"**Depth:** {prefs.get('summary_depth', 'Standard')}")
                st.write(f"**Style:** {prefs.get('interaction_style', 'Neutral')}")
                
                st.markdown("#### 📜 Recent History")
                history = ctx.get('session_history', [])
                if history:
                    # Create a simple list of recent actions
                    for i, item in enumerate(reversed(history[-5:])): # Show last 5
                        icon = "📝" if item['type'] == 'summary_generated' else "❓"
                        details = item.get('details', {}) or {}
                        goal = details.get('goal', '')
                        query = item.get('query', '')
                        
                        desc = f"{goal}" if goal else f"'{query}'"
                        st.text(f"{icon} {item['type'].replace('_', ' ').title()}\n   ↳ {desc}")
                        st.divider()
                else:
                    st.caption("No history yet.")
            else:
                st.write("No active profile.")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        return chunk_size, sensitivity, api_key, user_goal

def render_hero_section():
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    st.markdown(f"<h1 class='main-header'>{APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d; font-size: 1.2rem; margin-bottom: 2rem;'>Professional Document Intelligence & Analysis System</p>", unsafe_allow_html=True)

def render_analysis_tab(analyzer, chunks, user_goal="General Reading"):
    st.subheader("📊 Analysis Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Generate Executive Summary", use_container_width=True, type="primary"):
            with st.spinner("Analyzing content structure..."):
                st.session_state.analysis_results['summary'] = analyzer.generate_summary(user_goal=user_goal)
                
    with col2:
        if st.button("❓ Identify Key Questions", use_container_width=True):
            with st.spinner("Extracting key topics..."):
                st.session_state.analysis_results['questions'] = analyzer.generate_questions()
                
    with col3:
        if st.button("💡 Generate Smart FAQs", use_container_width=True):
            with st.spinner("Synthesizing Q&A pairs..."):
                st.session_state.analysis_results['faqs'] = analyzer.generate_faqs()
                
    # Display Results
    if st.session_state.analysis_results['summary']:
        st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
        st.markdown(st.session_state.analysis_results['summary'])
        st.markdown("</div>", unsafe_allow_html=True)
        
    if st.session_state.analysis_results['questions']:
        st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
        st.subheader("Key Inquiry Points")
        for i, q in enumerate(st.session_state.analysis_results['questions'], 1):
            st.markdown(f"**{i}.** {q}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    if st.session_state.analysis_results['faqs']:
        st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
        st.subheader("Frequently Asked Questions")
        for q, a in st.session_state.analysis_results['faqs']:
            with st.expander(f"📌 {q}"):
                st.markdown(a)
        st.markdown("</div>", unsafe_allow_html=True)


def render_analytics_tab(chunks):
    st.subheader("📈 Deep Insights")
    
    analytics = AnalyticsEngine(chunks)
    
    # 1. Complexity Score
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
        complexity = analytics.calculate_reading_complexity()
        st.metric("Reading Ease Score", complexity['score'])
        st.caption(f"Target Audience: {complexity['level']}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    # 2. Charts
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(analytics.generate_sentiment_arc(), use_container_width=True)
    with col4:
        st.plotly_chart(analytics.generate_word_distribution(), use_container_width=True)

def render_chat_tab(analyzer):
    st.subheader("💬 AI Assistant")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chat_history:
            st.info("👋 Hello! I've analyzed the document. Ask me anything about it.")
        
        for q, a in st.session_state.chat_history:
            st.markdown(f'<div class="chat-user">👤 <strong>You:</strong><br>{q}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-assistant">🤖 <strong>AI:</strong><br>{a}</div>', unsafe_allow_html=True)
            
    # Input area
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            user_input = st.text_input("Ask a question about the document:", placeholder="e.g., What is the main conclusion?")
        with col2:
            submit_button = st.form_submit_button("Send 🚀", use_container_width=True)
            
        if submit_button and user_input:
            with st.spinner("Thinking..."):
                answer = analyzer.answer_question(user_input)
                st.session_state.chat_history.append((user_input, answer))
                st.rerun()

def render_export_tab(chunks):
    st.subheader("📥 Export Center")
    if not st.session_state.analysis_results['summary']:
        st.warning("⚠️ Please generate an analysis (Summary, Questions, etc.) before exporting.")
        return

    col1, col2, col3 = st.columns(3)
    
    # Pack data
    summary = st.session_state.analysis_results['summary']
    questions = st.session_state.analysis_results.get('questions') or []
    faqs = st.session_state.analysis_results.get('faqs') or []
    history = st.session_state.chat_history
    
    with col1:
        st.download_button(
            "📄 Download TXT Report",
            data=create_txt_report(summary, questions, faqs, chunks, history),
            file_name=f"analysis_report_{int(time.time())}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    with col2:
        st.download_button(
            "💾 Download JSON Data",
            data=create_json_report(summary, questions, faqs, chunks, history),
            file_name=f"analysis_data_{int(time.time())}.json",
            mime="application/json",
            use_container_width=True
        )
        
    with col3:
        st.download_button(
            "🌐 Download HTML Report",
            data=create_html_report(summary, questions, faqs, chunks, history),
            file_name=f"analysis_report_{int(time.time())}.html",
            mime="text/html",
            use_container_width=True
        )

def main():
    st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout=LAYOUT_MODE)
    
    # State Init
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {'summary': None, 'questions': None, 'faqs': None}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    if 'processed_chunks' not in st.session_state:
        st.session_state.processed_chunks = None
        

    # Render UI
    chunk_size_setting, sensitivity, api_key, user_goal = render_sidebar()
    render_hero_section()
    
    uploaded_file = st.file_uploader("📂 Upload your PDF Document", type="pdf")
    
    if uploaded_file:
        # Processing Trigger
        # If we have chunks but analyzer doesn't match current API key state, we might need to update it.
        # For simplicity, we create the analyzer if chunks exist but analyzer is None, OR if we just processed.
        
        if st.session_state.processed_chunks is None:
            with st.spinner("🔄 Processing document..."):
                documents, pages = extract_text_from_pdf(uploaded_file)
                if documents:
                    chunks = chunk_documents(documents, chunk_size=chunk_size_setting)
                    st.session_state.processed_chunks = chunks
                    # Initialize Analyzer with API Key
                    st.session_state.analyzer = AnalysisEngine(chunks, api_key=api_key)
                    st.success(f"✅ Document processed: {pages} pages, {len(chunks)} analysis chunks.")
                else:
                    st.error("Failed to extract text.")
                    return
        
        # Recovery: If chunks exist but analyzer is lost (e.g. after code reload), re-init
        if st.session_state.processed_chunks is not None and st.session_state.analyzer is None:
             st.session_state.analyzer = AnalysisEngine(st.session_state.processed_chunks, api_key=api_key)
        
        # Ensure analyzer is updated if API key is added later
        if st.session_state.analyzer and api_key and isinstance(st.session_state.analyzer.llm_provider, type(None)): # Checking type strictly is hard, let's just re-init if user pushes a button? 
            # Actually, let's just re-init analyzer if the key provided differs from what's stored? 
            # For this MVP, let's just make sure we pass the key on creation. 
            pass


        
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis", "📈 Deep Insights", "💬 Assistant", "📥 Exports"])
        
        with tab1:
            render_analysis_tab(st.session_state.analyzer, st.session_state.processed_chunks, user_goal)
            
        with tab2:
            render_analytics_tab(st.session_state.processed_chunks)
            
        with tab3:
            render_chat_tab(st.session_state.analyzer)
            
        with tab4:
            render_export_tab(st.session_state.processed_chunks)
    else:
        # Reset state on file remove
        if st.session_state.processed_chunks is not None:
             st.session_state.analysis_results = {'summary': None, 'questions': None, 'faqs': None}
             st.session_state.chat_history = []
             st.session_state.analyzer = None
             st.session_state.processed_chunks = None
             st.rerun()

        st.info("👆 Please upload a PDF file to begin analysis.")
