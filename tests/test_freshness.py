import io

import pytest
from PIL import Image
from werkzeug.security import generate_password_hash

import app as farmdirect_app
import database


@pytest.fixture
def freshness_client(tmp_path, monkeypatch):
    database_path = tmp_path / "freshness_test.db"

    monkeypatch.setattr(
        database,
        "DATABASE",
        str(database_path),
    )

    database.init_db()

    farmdirect_app.app.config["TESTING"] = True
    farmdirect_app.app.config["SECRET_KEY"] = "freshness-test-secret"

    with farmdirect_app.app.test_client() as client:
        yield client


def create_user(role):
    conn = database.get_db_connection()

    cursor = conn.execute(
        """
        INSERT INTO users
        (name, email, password_hash, role, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Freshness Test User",
            f"{role}@freshness.test",
            generate_password_hash("password123"),
            role,
            "Active",
        ),
    )

    user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return user_id


def login_as(client, user_id, role):
    with client.session_transaction() as session:
        session["user_id"] = user_id
        session["name"] = "Freshness Test User"
        session["role"] = role


def make_test_image():
    image = Image.new(
        "RGB",
        (224, 224),
        (120, 180, 80),
    )

    buffer = io.BytesIO()

    image.save(buffer, format="JPEG")
    buffer.seek(0)

    return buffer


def test_freshness_requires_authentication(
    freshness_client,
):
    response = freshness_client.post(
        "/products/analyze-freshness"
    )

    assert response.status_code == 302


def test_non_farmer_cannot_analyze_freshness(
    freshness_client,
):
    user_id = create_user("consumer")

    login_as(
        freshness_client,
        user_id,
        "consumer",
    )

    response = freshness_client.post(
        "/products/analyze-freshness"
    )

    assert response.status_code == 302


def test_farmer_can_analyze_valid_image(
    freshness_client,
    monkeypatch,
):
    user_id = create_user("farmer")

    login_as(
        freshness_client,
        user_id,
        "farmer",
    )

    monkeypatch.setattr(
        farmdirect_app,
        "predict_freshness",
        lambda image: {
            "label": "Fresh",
            "confidence": 94.25,
        },
    )

    response = freshness_client.post(
        "/products/analyze-freshness",
        data={
            "freshness_image": (
                make_test_image(),
                "tomato.jpg",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["label"] == "Fresh"
    assert data["confidence"] == 94.25
    assert "AI-assisted" in data["message"]


def test_invalid_image_is_rejected(
    freshness_client,
):
    user_id = create_user("farmer")

    login_as(
        freshness_client,
        user_id,
        "farmer",
    )

    response = freshness_client.post(
        "/products/analyze-freshness",
        data={
            "freshness_image": (
                io.BytesIO(b"not an image"),
                "invalid.jpg",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False
    assert "valid image" in data["message"].lower()