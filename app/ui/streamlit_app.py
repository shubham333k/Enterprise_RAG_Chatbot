"""
Enterprise Knowledge Assistant — Streamlit MVP Frontend

Features:
- Login/logout with JWT
- Document upload with department/access-level tagging
- Chat interface with source citations
- Admin analytics dashboard
- Session management
"""
import streamlit as st
import requests
import json
import time
from datetime import datetime

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Enterprise Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000"

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    .css-1d391kg { background: #0f172a; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid #334155;
    }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    /* Chat bubbles */
    .chat-user {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 85%;
        margin-left: auto;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    .chat-assistant {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        color: #e2e8f0;
        border: 1px solid #334155;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 85%;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    /* Citation card */
    .citation-card {
        background: #1e293b;
        border: 1px solid #6366f1;
        border-left: 4px solid #6366f1;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 4px 0;
        font-size: 0.85rem;
        color: #94a3b8;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #6366f1;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 4px;
    }

    /* Role badge */
    .role-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 8px;
    }
    .role-admin { background: #dc2626; color: white; }
    .role-hr { background: #7c3aed; color: white; }
    .role-engineering { background: #0891b2; color: white; }
    .role-sales { background: #059669; color: white; }
    .role-employee { background: #64748b; color: white; }

    /* Input area */
    .stTextInput input, .stTextArea textarea {
        background: #1e293b;
        border: 1px solid #334155;
        color: #e2e8f0;
        border-radius: 8px;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
    }

    /* Success/Error messages */
    .stSuccess { background: #064e3b; border: 1px solid #059669; }
    .stError { background: #7f1d1d; border: 1px solid #dc2626; }

    /* Divider */
    hr { border-color: #334155; }

    /* Hide default streamlit menu */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── Session State Initialization ─────────────────────────────────────────────
def init_state():
    defaults = {
        "token": None,
        "username": None,
        "role": None,
        "messages": [],
        "session_id": f"sess_{int(time.time())}",
        "page": "chat",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─── API Helpers ──────────────────────────────────────────────────────────────
def api_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def api_post(endpoint, data=None, json_data=None, files=None, form_data=None):
    try:
        url = f"{API_URL}{endpoint}"
        headers = api_headers()
        if files:
            return requests.post(url, files=files, data=form_data, headers=headers, timeout=60)
        return requests.post(url, json=json_data or data, headers=headers, timeout=30)
    except requests.exceptions.ConnectionError:
        return None

def api_get(endpoint):
    try:
        return requests.get(f"{API_URL}{endpoint}", headers=api_headers(), timeout=15)
    except requests.exceptions.ConnectionError:
        return None


# ─── Auth Check ───────────────────────────────────────────────────────────────
def check_api_connection():
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


# ─── Login Page ───────────────────────────────────────────────────────────────
def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding: 40px 0 20px 0;">
            <div style="font-size: 4rem; margin-bottom: 10px;">🧠</div>
            <h1 class="main-header">Enterprise Knowledge Assistant</h1>
            <p style="color: #94a3b8; margin-bottom: 30px;">
                AI-Powered Document Intelligence Platform
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Connection check
        if not check_api_connection():
            st.error("⚠️ Cannot connect to the API server. Make sure the FastAPI backend is running:\n\n"
                     "```\nuvicorn app.api.main:app --reload --port 8000\n```")
            return

        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)

                if submitted:
                    r = requests.post(f"{API_URL}/auth/login",
                                      json={"username": username, "password": password}, timeout=10)
                    if r and r.status_code == 200:
                        data = r.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.username = data["username"]
                        st.session_state.role = data["role"]
                        st.success(f"Welcome back, {data['username']}!")
                        st.rerun()
                    else:
                        msg = r.json().get("detail", "Login failed") if r else "Server not reachable"
                        st.error(f"❌ {msg}")

            st.markdown("""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px; margin-top: 16px;">
                <p style="color: #94a3b8; font-size: 0.85rem; margin: 0; font-weight: 600;">Demo Accounts</p>
                <table style="width: 100%; color: #e2e8f0; font-size: 0.82rem; margin-top: 8px;">
                    <tr><td><b>admin</b></td><td>admin123</td><td style="color: #dc2626;">All access</td></tr>
                    <tr><td><b>hr_user</b></td><td>hr123</td><td style="color: #7c3aed;">HR docs</td></tr>
                    <tr><td><b>eng_user</b></td><td>eng123</td><td style="color: #0891b2;">Engineering</td></tr>
                    <tr><td><b>sales_user</b></td><td>sales123</td><td style="color: #059669;">Sales</td></tr>
                    <tr><td><b>employee</b></td><td>emp123</td><td style="color: #64748b;">Public only</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

        with tab_register:
            with st.form("register_form"):
                new_user = st.text_input("Username", placeholder="Choose a username")
                new_email = st.text_input("Email (optional)", placeholder="your@email.com")
                new_pass = st.text_input("Password", type="password", placeholder="Min 6 characters")
                new_role = st.selectbox("Role", ["employee", "sales", "engineering", "hr"])
                submitted_reg = st.form_submit_button("Create Account", use_container_width=True)

                if submitted_reg:
                    r = requests.post(f"{API_URL}/auth/register", json={
                        "username": new_user,
                        "password": new_pass,
                        "email": new_email or None,
                        "role": new_role,
                    }, timeout=10)
                    if r and r.status_code == 201:
                        data = r.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.username = data["username"]
                        st.session_state.role = data["role"]
                        st.success("Account created! Welcome.")
                        st.rerun()
                    else:
                        msg = r.json().get("detail", "Registration failed") if r else "Server error"
                        st.error(f"❌ {msg}")


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # User info
        role_colors = {
            "admin": "#dc2626", "hr": "#7c3aed", "engineering": "#0891b2",
            "sales": "#059669", "employee": "#64748b"
        }
        color = role_colors.get(st.session_state.role, "#64748b")
        st.markdown(f"""
        <div style="padding: 12px; background: #1e293b; border-radius: 10px; margin-bottom: 16px; border: 1px solid #334155;">
            <div style="font-weight: 600; color: #e2e8f0;">👤 {st.session_state.username}</div>
            <div style="margin-top: 4px;">
                <span style="background: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{st.session_state.role.upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Navigation")
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
        if st.button("📄 Documents", use_container_width=True):
            st.session_state.page = "documents"
            st.rerun()
        if st.session_state.role == "admin":
            if st.button("📊 Analytics", use_container_width=True):
                st.session_state.page = "analytics"
                st.rerun()

        st.markdown("---")

        # Upload section (all roles)
        st.markdown("### 📤 Upload Document")
        uploaded = st.file_uploader(
            "Choose a file",
            type=["pdf", "docx", "xlsx", "csv", "txt", "md"],
            accept_multiple_files=False,
            help="PDF, DOCX, XLSX, CSV, TXT, or MD files up to 50 MB",
        )

        if uploaded:
            dept = st.selectbox("Department", ["public", "hr", "engineering", "sales", "legal", "finance"])
            access = st.selectbox("Access Level", ["public", "hr", "engineering", "sales", "legal"])

            col_up, col_idx = st.columns(2)
            with col_up:
                if st.button("Upload", use_container_width=True):
                    with st.spinner("Uploading..."):
                        r = api_post("/documents/upload",
                                     files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)},
                                     form_data={"department": dept, "access_level": access})
                        if r and r.status_code == 201:
                            data = r.json()
                            st.session_state["last_doc_id"] = data["document_id"]
                            st.success(f"✅ Uploaded! ID: {data['document_id']}")
                        else:
                            st.error("Upload failed")

            with col_idx:
                if st.button("Index", use_container_width=True):
                    doc_id = st.session_state.get("last_doc_id")
                    if doc_id:
                        with st.spinner("Indexing..."):
                            r = api_post("/documents/index", json_data={
                                "document_id": doc_id,
                                "department": dept,
                                "access_level": access,
                            })
                            if r and r.status_code == 200:
                                data = r.json()
                                st.success(f"✅ Indexed! {data.get('chunk_count', 0)} chunks")
                            else:
                                err = r.json() if r else "Connection error"
                                st.error(f"❌ {err}")
                    else:
                        st.warning("Upload a file first")

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in ["token", "username", "role", "messages"]:
                st.session_state[key] = None if key != "messages" else []
            st.rerun()


# ─── Chat Page ────────────────────────────────────────────────────────────────
def render_chat():
    st.markdown('<h1 class="main-header">🧠 Enterprise Knowledge Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; margin-bottom: 24px;">Ask questions about your enterprise documents. Every answer is cited.</p>', unsafe_allow_html=True)

    # Chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">💬 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-assistant">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
                if msg.get("citations"):
                    with st.expander(f"📚 {len(msg['citations'])} Source(s)", expanded=False):
                        for c in msg["citations"]:
                            page_str = f"· Page {c['page']}" if c.get("page") else ""
                            section_str = f"· {c['section']}" if c.get("section") else ""
                            score_str = f"· Relevance: {c.get('score', 0):.0%}" if c.get("score") else ""
                            st.markdown(f"""
                            <div class="citation-card">
                                📄 <b>{c['document']}</b> {page_str} {section_str} {score_str}
                                <br><small style="color: #64748b;">{c.get('excerpt', '')[:150]}...</small>
                            </div>
                            """, unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Ask about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("🤖 Thinking..."):
            start = time.time()
            r = api_post("/chat/query", json_data={
                "question": prompt,
                "session_id": st.session_state.session_id,
                "top_k": 5,
            })
            elapsed = int((time.time() - start) * 1000)

        if r and r.status_code == 200:
            data = r.json()
            answer = data.get("answer", "No answer returned.")
            citations = data.get("citations", [])
            latency = data.get("latency_ms", elapsed)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "citations": citations,
            })

            # Show latency badge
            st.caption(f"⚡ Response time: {latency}ms · {len(citations)} source(s) found")
        elif r is None:
            st.error("❌ Cannot reach the API. Is the backend running?")
        else:
            err = r.json().get("detail", "Query failed") if r else "Unknown error"
            st.error(f"❌ Error: {err}")

        st.rerun()

    # Quick example queries
    if not st.session_state.messages:
        st.markdown("---")
        st.markdown("### 💡 Try asking...")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("What is the maternity leave policy?", use_container_width=True):
                st.session_state._quick_q = "What is the maternity leave policy?"
        with col2:
            if st.button("What are the engineering code review guidelines?", use_container_width=True):
                st.session_state._quick_q = "What are the engineering code review guidelines?"
        with col3:
            if st.button("What is the sales commission structure?", use_container_width=True):
                st.session_state._quick_q = "What is the sales commission structure?"


# ─── Documents Page ───────────────────────────────────────────────────────────
def render_documents():
    st.markdown('<h1 class="main-header">📄 Document Library</h1>', unsafe_allow_html=True)

    r = api_get("/documents")
    if r and r.status_code == 200:
        docs = r.json()
        if not docs:
            st.info("No documents uploaded yet. Use the sidebar to upload your first document.")
            return

        # Stats row
        indexed = sum(1 for d in docs if d.get("status") == "indexed")
        total_chunks = sum(d.get("chunk_count", 0) for d in docs)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(docs)}</div><div class="metric-label">Total Documents</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{indexed}</div><div class="metric-label">Indexed</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{total_chunks:,}</div><div class="metric-label">Total Chunks</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        for doc in docs:
            status_icon = "✅" if doc["status"] == "indexed" else "⏳" if doc["status"] == "uploaded" else "❌"
            with st.expander(f"{status_icon} **{doc['file_name']}** · {doc['access_level']} · {doc['chunk_count']} chunks"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**Type:** {doc['file_type'].upper()}")
                c2.markdown(f"**Department:** {doc['department']}")
                c3.markdown(f"**Status:** {doc['status']}")
                if doc.get("created_at"):
                    st.caption(f"Uploaded: {doc['created_at'][:10]}")
    else:
        st.error("Failed to load documents. Check API connection.")


# ─── Analytics Page ───────────────────────────────────────────────────────────
def render_analytics():
    st.markdown('<h1 class="main-header">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)

    r = api_get("/analytics/overview")
    if r and r.status_code == 200:
        data = r.json()

        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{data["total_queries"]:,}</div><div class="metric-label">Total Queries</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{data["total_documents"]}</div><div class="metric-label">Documents</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{data["avg_latency_ms"]:.0f}ms</div><div class="metric-label">Avg Latency</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{data["no_answer_rate"]}%</div><div class="metric-label">No-Answer Rate</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("#### 🔥 Top Questions")
            for q in data.get("top_questions", [])[:8]:
                st.markdown(f"- `{q['count']}x` {q['question'][:80]}...")

        with col_right:
            st.markdown("#### 👥 Queries by Role")
            for role, count in data.get("queries_by_role", {}).items():
                pct = count / max(data["total_queries"], 1) * 100
                st.progress(pct / 100, text=f"{role}: {count} ({pct:.0f}%)")

        st.markdown("---")
        st.markdown("#### 🕐 Recent Queries")
        recent = data.get("recent_queries", [])
        if recent:
            for q in recent[:10]:
                icon = "✅" if q.get("has_answer") else "❓"
                st.markdown(f"{icon} `{q.get('role', '?')}` · **{q['question'][:70]}** · {q.get('latency_ms', 0)}ms")
    elif r and r.status_code == 403:
        st.error("❌ Analytics is restricted to Admins only.")
    else:
        st.error("Failed to load analytics.")


# ─── Main App ─────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.token:
        render_login()
    else:
        render_sidebar()

        page = st.session_state.get("page", "chat")
        if page == "chat":
            render_chat()
        elif page == "documents":
            render_documents()
        elif page == "analytics":
            render_analytics()


if __name__ == "__main__":
    main()
