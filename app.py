import streamlit as st
from mock_data import MOCK_TASKS,  MOCK_USER, MOCK_TOKEN
import api_client
import time
import pandas as pd
import plotly.express as px


# Step 1: Streamlit page configuration 
st.set_page_config( 
    page_title="AI Dashboard", 
    page_icon="🤖",
    layout="wide"
)
#Step 2: Session state initialization 
if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

if "use_mock" not in st.session_state:
    st.session_state.use_mock = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mock_tasks" not in st.session_state:
    st.session_state.mock_tasks = [
        task.copy() for task in MOCK_TASKS
    ]

#Retrieve tasks from FastAPI/ mock session data.
def load_tasks():
    
    if st.session_state.use_mock:
        return st.session_state.mock_tasks.copy(), None

    return api_client.get_tasks(st.session_state.token)

#() to calculate task statistics
def calculate_stats(tasks):

    total = len(tasks)

    done = sum(
        1 for task in tasks if task["done"]
    )

    pending = total - done

    return {
        "total": total,
        "done": done,
        "pending": pending
    }

#Display dashboard metrics, dataframe & chart.
def show_dashboard(tasks):

    st.header("📊 Task Dashboard")

    stats = calculate_stats(tasks)

    #Three metric cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Tasks", stats["total"])

    with col2:
        st.metric("Completed Tasks", stats["done"])

    with col3:
        st.metric("Pending Tasks", stats["pending"])

    st.divider()

    #Task dataframe
    st.subheader("Task Overview")

    if tasks:
        df = pd.DataFrame(tasks)

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )
    else:
        st.info("No tasks found.")

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
        text="Count",
        title="Completed vs Pending Tasks"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        fig,
        width="stretch",
        key="task_completion_chart"
    )

#Create tasks and toggle task completion
def show_task_management(tasks):

    st.header("✅ Task Management")

    st.subheader("Create New Task")

    with st.form("create_task_form", clear_on_submit=True):
        title = st.text_input("Task title")
        submitted = st.form_submit_button("Add Task")

    if submitted:
        if not title.strip():
            st.warning("Please enter a task title.")

        elif st.session_state.use_mock:
            new_id = max(
                (task["id"] for task in st.session_state.mock_tasks),
                default=0
            ) + 1

            st.session_state.mock_tasks.append({
                "id": new_id,
                "title": title.strip(),
                "done": False,
                "user": st.session_state.username
            })

            st.rerun()

        else:
            new_task, error = api_client.create_task(
                st.session_state.token,
                title.strip()
            )

            if error:
                st.error(error)
            else:
                st.rerun()

    st.divider()

    st.subheader("Your Tasks")

    if not tasks:
        st.info("No tasks available.")
        return

    for task in tasks:
        col1, col2, col3 = st.columns([1, 6, 2])

        with col1:
            st.write(f"# {task['id']}")

        with col2:
            status = "✅" if task["done"] else "⏳"
            st.write(f"{status} {task['title']}")

        with col3:
            button_label = (
                "Mark Pending" if task["done"] 
                else "Mark Complete" 
            )

            if st.button(
                button_label, 
                key=f"task_{task['id']}"
            ):
                if st.session_state.use_mock:
                    for mock_task in st.session_state.mock_tasks:
                        if mock_task["id"] == task["id"]:
                            mock_task["done"] = not mock_task["done"]
                            break

                    st.rerun()
                else:
                    updated_task, error = api_client.complete_task(
                        st.session_state.token,
                        task["id"]
                    )
                    if error:
                        st.error(error)
                    else:
                        st.rerun()
    st.divider()

    st.caption(
        "Task changes are stored in the FastAPI backend. "
        "Because the backend uses in-memory storage, "
        "tasks reset when the backend restarts."
    )

# ═════════════════════════════════
# SECTION D — AUTHENTICATION
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
            value=False
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
                st.session_state.mock_tasks = [
                    task.copy() for task in MOCK_TASKS
                ]
                st.rerun()
            else:
                st.error("Invalid demo credentials.")
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

# SECTION E — SIDEBAR
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
        value="You are a helpful AI assistant."
    )

    st.caption("Module 6 Final Project")

# ══════════════════════════════════
# SECTION F — MAIN CONTENT 
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

with st.spinner("Loading tasks..."):
    tasks, error = load_tasks()


if error:
    st.error(error)

    if "HTTP 401" in error:
        st.session_state.token = None
        st.session_state.username = None
        st.session_state.use_mock = False
        st.warning(
            "Your session has expired. Please log in again."
        )

    st.stop()

with tab_dash:
    show_dashboard(tasks)

with tab_tasks:
    show_task_management(tasks)

with tab_chat:
    st.header("🤖 AI Chat")

    st.info(
        "AI chat functionality wi ll be "
        "implemented in Phase 6."
    )

# ── TAB 3: AI Chat ───────────────────

