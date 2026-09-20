import os
import sys
import tempfile

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import pytest
from werkzeug.security import check_password_hash

import database
import app as farmdirect_app


@pytest.fixture
def client(monkeypatch):
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)

    monkeypatch.setattr(database, "DATABASE", db_path)

    database.init_db()

    farmdirect_app.app.config["TESTING"] = True
    farmdirect_app.app.config["SECRET_KEY"] = "security-test-secret"

    with farmdirect_app.app.test_client() as client:
        yield client

    os.unlink(db_path)


def create_user(name, email, password, role, status="Active"):
    from werkzeug.security import generate_password_hash

    conn = database.get_db_connection()

    cursor = conn.execute(
        """
        INSERT INTO users
        (name, email, password_hash, role, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            email,
            generate_password_hash(password),
            role,
            status,
        ),
    )

    user_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return user_id


def login(client, email, password):
    return client.post(
        "/login",
        data={
            "email": email,
            "password": password,
        },
        follow_redirects=True,
    )


# --------------------------------
# Password security
# --------------------------------

def test_password_is_hashed(client):
    password = "password123"

    create_user(
        "Test User",
        "security@example.com",
        password,
        "consumer",
    )

    conn = database.get_db_connection()

    user = conn.execute(
        """
        SELECT password_hash
        FROM users
        WHERE email = ?
        """,
        ("security@example.com",),
    ).fetchone()

    conn.close()

    assert user is not None
    assert user["password_hash"] != password
    assert check_password_hash(
        user["password_hash"],
        password,
    )


# --------------------------------
# Authentication protection
# --------------------------------

def test_invalid_login_does_not_create_session(client):
    create_user(
        "Test User",
        "security@example.com",
        "password123",
        "consumer",
    )

    response = login(
        client,
        "security@example.com",
        "wrong-password",
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session
        assert "role" not in session


def test_inactive_account_cannot_login(client):
    create_user(
        "Inactive User",
        "inactive@example.com",
        "password123",
        "consumer",
        status="Inactive",
    )

    response = login(
        client,
        "inactive@example.com",
        "password123",
    )

    assert response.status_code == 200
    assert b"Your account is inactive." in response.data

    with client.session_transaction() as session:
        assert "user_id" not in session


# --------------------------------
# Role-based access control
# --------------------------------

def test_unauthenticated_user_cannot_access_marketplace(client):
    response = client.get("/marketplace")

    assert response.status_code in (302, 403)


def test_farmer_cannot_access_consumer_cart(client):
    create_user(
        "Farmer",
        "farmer@example.com",
        "password123",
        "farmer",
    )

    login(
        client,
        "farmer@example.com",
        "password123",
    )

    response = client.get("/cart")

    assert response.status_code in (302, 403)


def test_consumer_cannot_access_farmer_product_management(client):
    create_user(
        "Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(
        client,
        "consumer@example.com",
        "password123",
    )

    response = client.get("/products")

    assert response.status_code in (302, 403)


def test_non_admin_cannot_access_admin_users(client):
    create_user(
        "Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(
        client,
        "consumer@example.com",
        "password123",
    )

    response = client.get("/admin/users")

    assert response.status_code in (302, 403)


def test_non_admin_cannot_access_admin_products(client):
    create_user(
        "Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(
        client,
        "consumer@example.com",
        "password123",
    )

    response = client.get("/admin/products")

    assert response.status_code in (302, 403)


# --------------------------------
# Unauthorized URL access
# --------------------------------

def test_farmer_cannot_view_another_users_product_edit_page(client):
    from werkzeug.security import generate_password_hash

    farmer1_id = create_user(
        "Farmer One",
        "farmer1@example.com",
        "password123",
        "farmer",
    )

    create_user(
        "Farmer Two",
        "farmer2@example.com",
        "password123",
        "farmer",
    )

    conn = database.get_db_connection()

    cursor = conn.execute(
        """
        INSERT INTO products
        (
            seller_id,
            name,
            category,
            quantity,
            price,
            location,
            quality_details,
            availability
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            farmer1_id,
            "Private Product",
            "Grains",
            100,
            50,
            "Delhi",
            "Good",
            "Available",
        ),
    )

    product_id = cursor.lastrowid

    conn.commit()
    conn.close()

    login(
        client,
        "farmer2@example.com",
        "password123",
    )

    response = client.get(
        f"/products/edit/{product_id}"
    )

    assert response.status_code == 302
    assert b"" != response.data


# --------------------------------
# Input validation
# --------------------------------

def test_product_rejects_negative_price(client):
    create_user(
        "Farmer",
        "farmer@example.com",
        "password123",
        "farmer",
    )

    login(
        client,
        "farmer@example.com",
        "password123",
    )

    response = client.post(
        "/products/add",
        data={
            "name": "Test Product",
            "category": "Grains",
            "quantity": "10",
            "price": "-50",
            "location": "Delhi",
            "quality_details": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Price must be a positive number." in response.data


def test_product_rejects_missing_required_fields(client):
    create_user(
        "Farmer",
        "farmer@example.com",
        "password123",
        "farmer",
    )

    login(
        client,
        "farmer@example.com",
        "password123",
    )

    response = client.post(
        "/products/add",
        data={
            "name": "",
            "category": "",
            "quantity": "",
            "price": "",
            "location": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert (
        b"Product name, category, quantity, price, and location are required."
        in response.data
    )


def test_cart_rejects_non_numeric_quantity(client):
    create_user(
        "Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(
        client,
        "consumer@example.com",
        "password123",
    )

    response = client.post(
        "/cart/add/999999",
        data={
            "quantity": "abc",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Quantity must be a positive whole number." in response.data


# --------------------------------
# SQL injection protection
# --------------------------------

def test_login_sql_injection_attempt_is_rejected(client):
    response = client.post(
        "/login",
        data={
            "email": "' OR '1'='1",
            "password": "' OR '1'='1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session
        assert "role" not in session


def test_marketplace_search_sql_injection_is_safe(client):
    create_user(
        "Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(
        client,
        "consumer@example.com",
        "password123",
    )

    response = client.get(
        "/marketplace?search=%27%20OR%201%3D1"
    )

    assert response.status_code == 200


# --------------------------------
# Session handling
# --------------------------------

def test_logout_clears_session(client):
    create_user(
        "Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(
        client,
        "consumer@example.com",
        "password123",
    )

    with client.session_transaction() as session:
        assert "user_id" in session
        assert "role" in session

    response = client.get(
        "/logout",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session
        assert "role" not in session