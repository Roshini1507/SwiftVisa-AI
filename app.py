import streamlit as st
from utils.rag import generate_eligibility

st.set_page_config(page_title="SwiftVisa AI", layout="wide")

st.title("SwiftVisa AI Assistant")
st.caption("AI-powered visa eligibility screening using policy-based reasoning")

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "step" not in st.session_state:
    st.session_state.step = 0

if "profile" not in st.session_state:
    st.session_state.profile = {}

if "result" not in st.session_state:
    st.session_state.result = None

# ---------------- QUESTIONS ----------------
questions = [
    ("age", "What is your age?"),
    ("nationality", "What is your nationality?"),
    ("education", "What is your highest education level?"),
    ("employment", "What is your current occupation?"),
    ("income", "What is your annual income (USD)?"),
    ("country", "Which country are you applying to?"),
    ("visa_type", "Which visa type are you applying for? (example: h1b)")
]

# ---------------- INIT FIRST QUESTION ----------------
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": questions[0][1]
    })

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- CHAT INPUT ----------------
user_input = st.chat_input("Type your answer...")

if user_input:

    # Save user input
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    key, _ = questions[st.session_state.step]
    st.session_state.profile[key] = user_input
    st.session_state.step += 1

    # ---------------- NEXT QUESTION ----------------
    if st.session_state.step < len(questions):

        next_q = questions[st.session_state.step][1]

        st.session_state.messages.append({
            "role": "assistant",
            "content": next_q
        })

    # ---------------- FINAL RESULT ----------------
    else:

        with st.spinner("Analyzing visa eligibility..."):
            response, docs = generate_eligibility(st.session_state.profile)

        st.session_state.result = (response, docs)

        status = ""
        explanation = ""

        for line in response.split("\n"):

            if "Eligibility Status" in line:
                status = line.split(":", 1)[1].strip()

            elif "Explanation" in line:
                explanation += line.split(":", 1)[1].strip() + " "

        result_ui = f"""
### Eligibility Result

**Status:** {status}

**Explanation:**  
{explanation}
"""

        st.session_state.messages.append({
            "role": "assistant",
            "content": result_ui
        })

    st.rerun()

# ---------------- RESULT DASHBOARD ----------------
if st.session_state.result:

    response, docs = st.session_state.result

    status = ""
    explanation = ""
    confidence = "0"
    relevance = "0"

    lines = response.split("\n")

    capture_explanation = False

    for line in lines:

        clean = line.strip()
        lower = clean.lower()

        # -------- STATUS --------
        if lower.startswith("eligibility status"):
            status = clean.split(":", 1)[1].strip()

        # -------- EXPLANATION (SAME LINE CASE) --------
        elif lower.startswith("explanation:"):
            explanation = clean.split(":", 1)[1].strip()
            capture_explanation = True

        # -------- EXPLANATION (MULTI-LINE CASE) --------
        elif lower.startswith("explanation"):
            capture_explanation = True
            explanation = ""
            continue

        # -------- STOP EXPLANATION --------
        elif lower.startswith("policy references") \
            or lower.startswith("missing information") \
            or lower.startswith("confidence score") \
            or lower.startswith("relevance score"):

            capture_explanation = False

        # -------- CAPTURE MULTI-LINE --------
        elif capture_explanation:
            explanation += " " + clean

        # -------- SCORES --------
        if "confidence score" in lower:
            val = clean.split(":", 1)[1].strip().replace("%", "")
            confidence = val if val else "0"

        if "relevance score" in lower:
            val = clean.split(":", 1)[1].strip().replace("%", "")
            relevance = val if val else "0"

    # cleanup
    explanation = explanation.strip()

    st.markdown("---")
    st.subheader("Eligibility Analysis")

    col1, col2, col3 = st.columns(3)
    col1.metric("Status", status)
    col2.metric("Confidence", f"{confidence}%")
    col3.metric("Relevance", f"{relevance}%")

    st.markdown("### Explanation")
    st.markdown(f"""
    <div style="
    padding:15px;
    border-radius:10px;
    background-color:#eef6ff;
    font-size:16px;
    ">
    {explanation}
    </div>
    """, unsafe_allow_html=True)

    if docs:
        with st.expander("Policy Sources (RAG)"):
            for doc in docs[:3]:
                st.markdown(f"**{doc.metadata.get('source_file','Unknown')}**")
                st.caption(doc.page_content[:200] + "...")

    if st.button("Start New Evaluation"):
        st.session_state.clear()
        st.rerun()