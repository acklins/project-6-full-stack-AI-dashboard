import streamlit as st
from mock_data import MOCK_TASKS, MOCK_STATS, MOCK_USER, MOCK_TOKEN
import api_client
import time

# Step 1: Streamlit page configuration 
st.set_page_config(
    layout="wide", 
    page_title="AI Dashboard", page_icon="🤖"
)
#Step 2: Session state initialization 
if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "use_mock" not in st.session_state:
    st.session_state.use_mock = False

# ═════════════════════════════════
# SECTION A — AUTHENTICATION
# ═════════════════════════════════
if not st.session_state.token:

    st.title("🔐 AI Dashboard Login")

    st.write("Sign in to access your dashboard.")

    with st.form("login_form"):

        username = st.text_input("Username")

        password = st.text_input(
            "Password", 
            type="password"
        )
        use_mock = st.checkbox(
            "Use Mock Data",
            value=True
        )

        login_button = st.form_submit_button("Login")

    if login_button:

        if not username or not password:
            st.error("Please enter a username and password.")

        elif use_mock:

            if username == "demo" and password == "demo":

                st.session_state.token = MOCK_TOKEN
                st.session_state.username = MOCK_USER
                st.session_state.use_mock = True

                st.rerun()
            else:
                st.error("Invalid username or password.")
        else:

            token, error = api_client.login(
                username,
                password
            )

            if error:
                st.error(error)

            elif token:
                st.session_state.token = token
                st.session_state.username = username
                st.session_state.use_mock = False

                st.rerun()
    st.stop()

# SECTION B — SIDEBAR
# ════════════════════════════════════
with st.sidebar:

    st.title("🤖 AI Dashboard")

    st.divider()

    st.success(
        f"Logged in as: {st.session_state.username}"
    )
    if st.button("🚪Logout"):

        st.session_state.token = None
        st.session_state.username = None
        st.session_state.use_mock = False
        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.subheader("AI Chat Settings")

    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful assistant."
    )

    st.caption("Module 6 Final Project")

# ══════════════════════════════════
# SECTION C — MAIN CONTENT (tabs)
# ═════════════════════════════════
st.title("📊 Welcome to the AI Dashboard!")

st.write(
    f"Hello, {st.session_state.username}! "
    "You have successfully logged in."
)

st.info(
    "Authentication is working. "
    "Dashboard features will be added in Phase 3."
)

# TODO tab_dash, tab_tasks, tab_chat = st.tabs(["📊 Dashboard", "✅ Tasks", "🤖 AI Chat"])

# ── TAB 1: Dashboard ──────────────────────────────────────────────────────
# TODO: with tab_dash:
#   - Load tasks (or use MOCK_TASKS if in mock mode)
#   - Show 3 st.metric() in 3 columns: total, done, pending
#   - Show st.dataframe() with task data
#   - Show a bar chart of done vs pending

# ── TAB 2: Tasks ──────────────────────────────────────────────────────────
# TODO: with tab_tasks:
#   - Add task form (POST to API or append to mock data)
#   - Task list with Complete buttons (PATCH to API or update mock)
#   - Error handling for API failures

# ── TAB 3: AI Chat ────────────────────────────────────────────────────────
# TODO: with tab_chat:
#   - Render chat history (st.chat_message for each message)
#   - st.chat_input for user messages
#   - Mock response generator or real OpenAI call
#   - st.write_stream for streaming display
#   - Append both user and assistant messages to session state
