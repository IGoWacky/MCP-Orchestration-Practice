import pytest

import app as app_module
from app import app, tasks


@pytest.fixture
def client():
    """Provide a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset task data and identifiers before each test."""
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Project-1 Report"},
        {"id": 2, "title": "Project-2 MMFs"}
    ])
    app_module.next_id = 3


def test_index(client):
    """Render the task tracker page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Tracker" in response.data


def test_get_tasks(client):
    """Return all tasks with a Medium fallback priority."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(task['priority'] == 'Medium' for task in data)


@pytest.mark.parametrize('priority', ['Low', 'Medium', 'High'])
def test_add_task_with_priority(client, priority):
    """Create and return a task for every supported priority."""
    response = client.post(
        '/api/tasks',
        json={"title": "Prioritized task", "priority": priority}
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == priority

    get_response = client.get('/api/tasks')
    created_task = get_response.get_json()[-1]
    assert created_task['priority'] == priority


def test_add_task_defaults_missing_priority_to_medium(client):
    """Default an omitted priority to Medium."""
    response = client.post('/api/tasks', json={"title": "Default task"})

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


def test_add_task_defaults_blank_priority_to_medium(client):
    """Default a blank priority to Medium."""
    response = client.post(
        '/api/tasks',
        json={"title": "Blank priority task", "priority": "  "}
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


def test_add_task_rejects_invalid_priority(client):
    """Reject priorities outside the supported values."""
    response = client.post(
        '/api/tasks',
        json={"title": "Invalid task", "priority": "Urgent"}
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_add_task_rejects_non_string_priority(client):
    """Reject non-string priority values with a client error."""
    response = client.post(
        '/api/tasks',
        json={"title": "Invalid task", "priority": ["High"]}
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_add_task_success(client):
    """Create a task without changing existing request behavior."""
    response = client.post('/api/tasks', json={"title": "Test new task"})
    assert response.status_code == 201
    assert response.get_json()['title'] == "Test new task"
    get_response = client.get('/api/tasks')
    assert len(get_response.get_json()) == 3


def test_add_task_missing_title(client):
    """Reject requests that do not include a title."""
    response = client.post('/api/tasks', json={"wrong_key": "value"})
    assert response.status_code == 400
    assert "error" in response.get_json()
    response2 = client.post('/api/tasks', json={})
    assert response2.status_code == 400


def test_frontend_supports_priority_controls_and_display(client):
    """Expose priority controls and rendering behavior in the frontend."""
    index_response = client.get('/')
    assert b'id="task-priority"' in index_response.data
    assert b'value="Low"' in index_response.data
    assert b'value="Medium"' in index_response.data
    assert b'value="High"' in index_response.data

    script_response = client.get('/static/app.js')
    assert b'task.priority || \'Medium\'' in script_response.data
    assert b'priority-${priorityClass}' in script_response.data


def test_delete_task(client):
    """Delete an existing task."""
    response = client.delete('/api/tasks/1')
    assert response.status_code == 200
    get_response = client.get('/api/tasks')
    data = get_response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == 2
