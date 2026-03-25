from pathlib import Path
import sys
from copy import deepcopy
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))

from fastapi.testclient import TestClient
from app import app, activities

# Backup the initial in-memory activities state
INITIAL_ACTIVITIES = deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))

@pytest.fixture
def client():
    return TestClient(app)


def test_signup_success_aaa(client):
    # Arrange
    activity_name = 'Chess Club'
    email = 'newstudent@mergington.edu'

    # Act
    resp = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert 'Signed up' in resp.json()['message']
    updated = client.get('/activities').json()[activity_name]['participants']
    assert email in updated


def test_duplicate_signup_rejected_aaa(client):
    # Arrange
    activity_name = 'Programming Class'
    email = 'duplicate@mergington.edu'
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    resp = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 400
    assert 'already signed up' in resp.json()['detail']


def test_delete_signup_success_aaa(client):
    # Arrange
    activity_name = 'Art Club'
    email = 'todelete@mergington.edu'
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    resp = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert 'Unregistered' in resp.json()['message']
    updated = client.get('/activities').json()[activity_name]['participants']
    assert email not in updated


def test_delete_unregistered_fails_aaa(client):
    # Arrange
    activity_name = 'Debate Team'
    email = 'nobody@mergington.edu'

    # Act
    resp = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 400
    assert 'not signed up' in resp.json()['detail']
