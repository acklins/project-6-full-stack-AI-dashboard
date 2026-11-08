Module 6 Final Project — AI Dashboard

Project Overview

The AI Dashboard is a full-stack task management application built with Streamlit and FastAPI. Users can authenticate, view task statistics, create tasks, update task completion status, and interact with a task-aware mock AI assistant.

Technologies Used

Python: Application programming language

Streamlit: Interactive frontend and dashboard

FastAPI: REST API backend

JWT (PyJWT): Signed authentication tokens

Requests: HTTP communication between Streamlit and FastAPI

Pandas: Task data presentation

Plotly: Interactive dashboard charts

Features:

Authentication

~Username/password login
~Signed JWT access tokens
~Token storage in Streamlit session state
~Protected backend endpoints
~Logout functionality
~Optional mock-data mode

Dashboard

~Total, completed, and pending task metrics
~Interactive task dataframe
~Plotly completion chart

Task Management

~Retrieve tasks using GET
~Create tasks using POST
~Toggle completion using PATCH
~Automatically refresh the dashboard after updates

AI Chat

~Task-aware mock assistant
~Streaming responses
~Conversation history
~Clear conversation
~Export conversation as a text file

Installation

Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate

Install dependencies:

python -m pip install -r requirements.txt

Create a .env file containing a securely generated JWT_SECRET_KEY.

Running the Application

Start the FastAPI backend:

python -m uvicorn backend:app --reload --port 8000

Start the Streamlit frontend in another terminal:

python -m streamlit run app.py

Open Streamlit at http://localhost:8501.

API documentation is available at http://127.0.0.1:8000/docs.

Demo Accounts:

For local classroom demonstration only:

Username: admin / Password: password123

Username: student / Password: learn2026

Architecture

Streamlit communicates with FastAPI through the centralized api_client.py module. The backend validates JWTs and manages task data. Streamlit displays the data and provides interactive task management and mock AI chat.

Known Limitations

~Tasks are stored in memory and reset when FastAPI restarts.

~Demo credentials are hardcoded and not appropriate for production.

~JWT logout clears the client session but does not revoke tokens.

~The AI assistant is rule-based rather than powered by a language model.

~The sidebar system prompt is not interpreted by the mock assistant.

Future Improvements

~Add SQLAlchemy database persistence.

~Implement password hashing and user registration.

~Add JWT refresh tokens and server-side revocation.

~Integrate a real AI model.

~Support task deadlines, categories, and priorities.

~Deploy the frontend and backend.
