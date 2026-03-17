import streamlit as st
import sys
import os

# Add src directory to path so we can import chatbot
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import ask_confessions

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Reformed Confessions Chatbot",
    page_icon="✝️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #8B4513;
        margin-bottom: 2rem;
    }
    .confession-badge {
        background-color: #8B4513;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    .disclaimer {
        background-color: #fff3cd !important;
        border-left: 4px solid #ffc107 !important;
        padding: 0.8rem !important;
        margin-top: 1rem !important;
        font-size: 0.85rem !important;
        border-radius: 0 4px 4px 0 !important;
        color: #856404 !important;
    }
    .disclaimer-explicit {
        background-color: #d4edda !important;
        border-left: 4px solid #28a745 !important;
        padding: 0.8rem !important;
        margin-top: 1rem !important;
        font-size: 0.85rem !important;
        border-radius: 0 4px 4px 0 !important;
        color: #155724 !important;
    }
    .section-header {
        color: #8B4513;
        font-weight: bold;
        margin-top: 1rem;
    }
    .citation-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }
    [data-baseweb="select"] {
        white-space: normal !important;
    }
    [data-baseweb="select"] span {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }
    [role="option"] {
        white-space: normal !important;
        word-wrap: break-word !important;
        height: auto !important;
        min-height: 2rem !important;
        padding: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="main-header">
    <h1>✝️ Reformed Confessions Chatbot</h1>
    <p>Ask what the historic confessions teach on any topic</p>
    <span class="confession-badge">Westminster Confession of Faith</span>
    <span class="confession-badge">London Baptist Confession 1689</span>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### About")
    st.markdown("""
    This chatbot answers theological questions exclusively 
    from the **Westminster Confession of Faith (WCF)** and 
    the **London Baptist Confession of 1689 (LBC)**.
    
    It will:
    - Cite specific chapters and sections
    - Distinguish explicit teaching from inference
    - Always include a disclaimer
    """)

    st.markdown("---")
    st.markdown("### Sample Questions")

    sample_questions = [
        "What do the confessions teach about justification?",
        "What do the confessions teach about Scripture?",
        "What do the confessions teach about prayer?",
        "What do the confessions teach about the Sabbath?",
        "What can be inferred about gender from the confessions?",
        "What can be inferred about Christian nationalism?",
    ]

    selected = st.selectbox(
        "Tap a question to load it:",
        ["👇 Choose a sample question..."] + sample_questions,
        key="sample_selectbox"
    )
    if selected and selected != "👇 Choose a sample question...":
        st.session_state.selected_question = selected

    st.markdown("---")
    st.markdown("### Built With")
    st.markdown("""
    - 🤖 Amazon Bedrock
    - 📚 Amazon Bedrock Knowledge Base
    - 🗄️ Amazon S3 Vectors
    - ⚡ AWS Lambda
    - 🐍 Python + Streamlit
    - 🤝 Built with [Claude](https://claude.ai) by Anthropic
    """)

# ============================================================
# CHAT HISTORY
# ============================================================

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'selected_question' not in st.session_state:
    st.session_state.selected_question = ""

# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

def format_answer(answer: str):
    """Format the answer splitting out the disclaimer for styled display."""
    disclaimer_a = "--- DISCLAIMER: This response is generated by artificial intelligence drawing directly"
    disclaimer_b = "--- DISCLAIMER: This is an artificially intelligent inference"

    disclaimer_text = ""
    main_answer = answer

    if disclaimer_a in answer:
        parts = answer.split("--- DISCLAIMER:")
        main_answer = parts[0].strip()
        disclaimer_text = "--- DISCLAIMER:" + parts[1]
        is_inference = False
    elif disclaimer_b in answer:
        parts = answer.split("--- DISCLAIMER:")
        main_answer = parts[0].strip()
        disclaimer_text = "--- DISCLAIMER:" + parts[1]
        is_inference = True
    else:
        is_inference = False

    return main_answer, disclaimer_text, is_inference


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            main_answer, disclaimer_text, is_inference = format_answer(message["content"])
            st.markdown(main_answer)
            if disclaimer_text:
                css_class = "disclaimer" if is_inference else "disclaimer-explicit"
                st.markdown(
                    f'<div class="{css_class}">{disclaimer_text}</div>',
                    unsafe_allow_html=True
                )
            if message.get("citations"):
                with st.expander(f"📖 {len(message['citations'])} source chunks retrieved"):
                    for i, citation in enumerate(message['citations'], 1):
                        st.markdown(
                            f'<div class="citation-box"><b>Source {i}:</b> {citation["content"]}...</div>',
                            unsafe_allow_html=True
                        )
        else:
            st.markdown(message["content"])

# ============================================================
# CHAT INPUT
# ============================================================

default_input = st.session_state.selected_question
if default_input:
    st.session_state.selected_question = ""

question = st.chat_input(
    "Ask what the confessions teach...",
)

if default_input and not question:
    question = default_input

# ============================================================
# PROCESS QUESTION
# ============================================================

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the confessions..."):
            result = ask_confessions(question)

        if result['success']:
            main_answer, disclaimer_text, is_inference = format_answer(result['answer'])

            st.markdown(main_answer)

            if disclaimer_text:
                css_class = "disclaimer" if is_inference else "disclaimer-explicit"
                st.markdown(
                    f'<div class="{css_class}">{disclaimer_text}</div>',
                    unsafe_allow_html=True
                )

            if result['citations']:
                with st.expander(f"📖 {len(result['citations'])} source chunks retrieved"):
                    for i, citation in enumerate(result['citations'], 1):
                        st.markdown(
                            f'<div class="citation-box"><b>Source {i}:</b> {citation["content"]}...</div>',
                            unsafe_allow_html=True
                        )

            st.session_state.messages.append({
                "role": "assistant",
                "content": result['answer'],
                "citations": result['citations']
            })

        else:
            error_msg = "Sorry, I encountered an error. Please try again."
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "citations": []
            })

# ============================================================
# CLEAR CHAT BUTTON
# ============================================================

if st.session_state.messages:
    if st.button("🗑️ Clear conversation", use_container_width=False):
        st.session_state.messages = []
        st.rerun()

# ============================================================
# COST NOTE
# ============================================================

st.markdown("---")
st.caption(
    "💡 Powered by Amazon Nova Micro on AWS Bedrock — "
    "each question costs a fraction of a cent to answer."
)