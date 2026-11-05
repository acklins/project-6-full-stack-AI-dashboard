import streamlit as st
from mock_data import MOCK_TASKS, MOCK_STATS, MOCK_USER, MOCK_TOKEN
import api_client
import time
import pandas as pd
import plotly.express as px


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

# Dashboard helper functions
def load_tasks():
    """Return sample tasks for the dashboard."""

    return MOCK_TASKS.copy()

#() to calculate task statistics
def calculate_stats(tasks):

    total_total = len(tasks)

    done_tasks = sum(
        1 for task in tasks if task["done"]
    )

    pending_tasks = total_total - done_tasks

    return {
        "total": total_total,
        "done": done_tasks,
        "pending": pending_tasks
    }

#Display dashboard metrics, table & chart.
def show_dashboard(tasks):

    st.header("📊 Task Dashboard")

    stats = calculate_stats(tasks)

    #Three metric cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total Tasks", 
            value=stats["total"]
        )

    with col2:
        st.metric(
            label="Completed Tasks", 
            value=stats["done"]
        )

    with col3:
        st.metric(
            label="Pending Tasks", 
            value=stats["pending"]
        )

    st.divider()

    #Task dataframe
    st.subheader("Task Overview")

    df = pd.DataFrame(tasks)

    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )

    st.divider()

    #Task status chart
    st.subheader("Task Completion Chart")

    chart_data = pd.DataFrame({
        "Status": ["Completed", "Pending"],
        "Count": [stats["done"], stats["pending"]]
    })

    fig = px.bar(
        chart_data,
        x="Status",
        y="Count",
        color="Status",
        title="Completed vs Pending Tasks",
        text="Count"
    )

    fig.update_layout(
        showlegend=False
    )

    st.plotly_chart(
        fig,
        width="stretch",
        key="task_completion_chart"
    )

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

st.title("🤖 AI Dashboard")

st.write(
    f"Welcome back, {st.session_state.username}!"
)
tab_dash, tab_tasks, tab_chat = st.tabs([
    "📊 Dashboard",
    "✅ Tasks",
    "🤖 AI Chat"
])

tasks = load_tasks()

with tab_dash:
    show_dashboard(tasks)

with tab_tasks:
    st.header("✅ Task Management")
    st.info(
        "Task creation and completion "
        "will be implemented in Phase 5."
    )

with tab_chat:
    st.header("🤖 AI Chat")
    st.info(
        "AI chat functionality "
        "will be implemented in Phase 6."
    )

# ── TAB 3: AI Chat ───────────────────
# TODO: with tab_chat:
#   - Render chat history (st.chat_message for each message)
#   - st.chat_input for user messages
#   - Mock response generator or real OpenAI call
#   - st.write_stream for streaming display
#   - Append both user and assistant messages to session state
