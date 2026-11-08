import requests

API_BASE = "http://127.0.0.1:8000"

#Send HTTP requests to the FastAPI backend.
def api_request(method, path, token=None, **kwargs):

    headers = kwargs.pop("headers", {})

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(
            method, 
            API_BASE + path, 
            headers=headers,
            timeout=10,
            **kwargs
        )

        if not response.ok:
            try:
                detail = response.json().get(
                    "detail", response.text
                )
            except ValueError:
                detail = response.text

            return None, f"HTTP {response.status_code}: {detail}"

        return response.json(), None

    except requests.ConnectionError:
        return None, "Cannot connect to FastAPI. Is itrunning?"

    except requests.Timeout:
        return None, "The API request time out."

    except requests.RequestException as exc:
        return None, f"API error: {exc}"

    except ValueError:
        return None, " invalid JSON response from API."
        ""

#login and return the access token
def login(username, password):
    data, error = api_request(
        "POST", 
        "/auth/token", 
        data={
            "username": username, "password": password
        }
    )

    if error:
        return None, error
    
    return data["access_token"], None

#Retrieve tasks for the logged-in user.
def get_tasks(token):

    return api_request(
        "GET", 
        "/tasks", 
        token=token
    )
#Create a new task
def create_task(token,title):

    return api_request(
        "POST",
        "/tasks",
        token=token,
        json={"title": title}
    )
#Toggle a taks's completion status.
def complete_task(token, task_id):

    return api_request(
        "PATCH",
        f"/tasks/{task_id}",
        token=token
    )

#Retrieve task statistics
def get_stats(token):
    return api_request(
        "GET",
        "/stats",
        token=token
    )