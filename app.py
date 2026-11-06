from numpy import full
import streamlit as st
from mock_data import MOCK_TASKS,  MOCK_USER, MOCK_TOKEN
import api_client
import time
import pandas as pd
import plotly.express as px
from datetime import datetime



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

#Generate a task aware mock AI response 
def generate_ai_response(prompt, tasks, system_prompt):

    question = prompt.lower().strip()
    stats = calculate_stats(tasks)

    total = stats["total"]
    done = stats["done"]
    pending = stats["pending"]

    pending_tasks = [
        task for task in tasks if not task["done"]
    ]

    completed_tasks = [
        task for task in tasks if task["done"]
    ]

    #Question about pending tasks
    if any(word in question for word in [
        "pending", "incomplete", "remaining", "unfinished"
    ]):

        if not pending_tasks:
            return "Excellent work! You have no pending tasks."

        task_list = "\n".join(
            f"- {task['title']}" 
            for task in pending_tasks
        )

        return(
            f"You currently have {pending} pending tasks: \n\n"
            f"{task_list}."
        )

    #Question about completed tasks
    elif any(word in question for word in [
        "completed", "finished", "done"
    ]):
        if not completed_tasks:
            return "You have not completed any tasks yet."

        task_list = "\n".join(
            f"- {task['title']}" 
            for task in completed_tasks
        )

        return(
            f"You have completed {done} tasks: \n\n"
            f"{task_list}"
        )

    #Question about overall progress
    elif any(word in question for word in [
        "summary", "progress", "status", "overview"
    ]):

        percentage = (
            round(done / total * 100, 1) 
            if total > 0 else 0
        )

        return (
            f"Here is your task progress summary:\n\n"
            f"- Total tasks: {total}\n"
            f"- Completed tasks: {done}\n"
            f"- Pending tasks: {pending}\n"
            f"- Completion rate: {percentage}%\n\n"
            f"Keep working through your pending tasks!"
        )

    #Question asking for suggestions
    elif any(word in question for word in [
        "suggest", "recommend", "priority", "next"
    ]):

        if not pending_tasks:
            return (
                "All your tasks are complete. "
                "Consider creating a new goal  "
                "And taking time to celebrate & rest!"
            )

        next_task = pending_tasks[0]["title"]

        return(
            f"My suggestion is to focus on:\n\n"
            f"**{next_task}**\n\n"
            f"Start with this pending task, break it into "
            f"smaller steps, and complete one step at a time."
        )

    #General fallback response
    else:
        return(
            "I am your AI Dashboard assistant.\n\n"
            "I can help you:\n"
            "- Summarize your task progress\n"
            "- List pending tasks\n"
            "- Review completed tasks\n"
            "- Suggest what to work on next\n\n"
            "Try asking: **What should I work on next?**"
        )

#Stream a mock AI response word by word
def stream_ai_response(response):

    for word in response.split(" "):
        yield word + " "
        time.sleep(0.04)

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

#Display AI chat with history and streaming
def show_ai_chat(tasks, system_prompt):

    st.header("🤖 AI Task Assistant")

    st.caption(
        "Mock AI assistant using your current task data."
    )

    #Chat controls
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Clear Conversation",
            key="clear_chat"
        ):

            st.session_state.messages = []
            st.rerun()

    with col2:
        export_text = ""

        for message in st.session_state.messages:
            role = message["role"].upper()
            content = message["content"]

            export_text += (
                f"{role}:\n{content}\n\n"
            )

        st.download_button(
            label="Download Conversation",
            data=export_text,
            file_name=(
                "ai_chat_"
                + datetime.now().strftime("%Y%m%d_%H%M%S")
                + ".txt"
            ),
            mime="text/plain",
            disabled=not st.session_state.messages
        )
    st.divider()

    #Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    #Chat input
    if prompt := st.chat_input(
        "Ask about your tasks..."
    ):
        #Save and display user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        #Generate and stream assistant response
        with st.chat_message("assistant"):

            response = generate_ai_response(
                prompt,
                tasks,
                system_prompt
            )

            full_response = st.write_stream(
                stream_ai_response(response)
            )
        #Save assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response
        })
        
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
        value=(
            "You are a helpful task management assistant. "
            "Help users understand their progress, "
            "identify pending tasks and plan next steps."
        ),
        height=120
    )

    st.caption(
        "Mock AI mode: responses are generated "
        "locally using task data."
    )

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

#AI Chat
with tab_dash:
    show_dashboard(tasks)

with tab_tasks:
    show_task_management(tasks)

with tab_chat:
    show_ai_chat(tasks, system_prompt)

    st.info(
        "AI chat functionality wi ll be "
        "implemented in Phase 6."
    )



