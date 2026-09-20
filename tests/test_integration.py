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
from werkzeug.security import generate_password_hash

import database
import app as farmdirect_app


@pytest.fixture
def client(monkeypatch):
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)

    monkeypatch.setattr(database, "DATABASE", db_path)

    database.init_db()

    farmdirect_app.app.config["TESTING"] = True
    farmdirect_app.app.config["SECRET_KEY"] = "integration-test-secret"

    with farmdirect_app.app.test_client() as client:
        yield client

    os.unlink(db_path)


def create_user(name, email, password, role):
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
            "Active",
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


def test_registration_to_login_flow(client):
    response = client.post(
        "/register",
        data={
            "name": "Integration Farmer",
            "email": "integration@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "role": "farmer",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    conn = database.get_db_connection()

    user = conn.execute(
        """
        SELECT id, email, role, status
        FROM users
        WHERE email = ?
        """,
        ("integration@example.com",),
    ).fetchone()

    conn.close()

    assert user is not None
    assert user["role"] == "farmer"
    assert user["status"] == "Active"

    response = login(
        client,
        "integration@example.com",
        "password123",
    )

    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_product_creation_is_saved_and_visible(client):
    farmer_id = create_user(
        "Integration Farmer",
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
            "name": "Integration Rice",
            "category": "Grains",
            "quantity": "100",
            "price": "50",
            "location": "Delhi",
            "quality_details": "Fresh",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    conn = database.get_db_connection()

    product = conn.execute(
        """
        SELECT *
        FROM products
        WHERE seller_id = ?
        AND name = ?
        """,
        (
            farmer_id,
            "Integration Rice",
        ),
    ).fetchone()

    conn.close()

    assert product is not None
    assert product["quantity"] == 100
    assert product["price"] == 50
    assert product["availability"] == "Available"


def test_product_to_cart_to_order_flow(client):
    farmer_id = create_user(
        "Integration Farmer",
        "farmer@example.com",
        "password123",
        "farmer",
    )

    consumer_id = create_user(
        "Integration Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
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
            farmer_id,
            "Integration Wheat",
            "Grains",
            20,
            40,
            "Delhi",
            "Fresh wheat",
            "Available",
        ),
    )

    product_id = cursor.lastrowid

    conn.commit()
    conn.close()

    login(
        client,
        "integration@example.com",
        "password123",
    )

    # The previous test does not share data, so login as consumer.
    client.post(
        "/login",
        data={
            "email": "integration@example.com",
            "password": "password123",
        },
    )

    # Clear session and log in as the consumer created above.
    client.get("/logout")

    login(
        client,
        "consumer@example.com",
        "password123",
    )

    response = client.post(
        f"/cart/add/{product_id}",
        data={"quantity": "2"},
        follow_redirects=True,
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert session["cart"][str(product_id)] == 2

    response = client.post(
        "/orders/place",
        follow_redirects=True,
    )

    assert response.status_code == 200

    conn = database.get_db_connection()

    order = conn.execute(
        """
        SELECT *
        FROM orders
        WHERE buyer_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (consumer_id,),
    ).fetchone()

    product = conn.execute(
        """
        SELECT quantity, availability
        FROM products
        WHERE id = ?
        """,
        (product_id,),
    ).fetchone()

    item = conn.execute(
        """
        SELECT *
        FROM order_items
        WHERE order_id = ?
        """,
        (order["id"],),
    ).fetchone()

    conn.close()

    assert order is not None
    assert order["status"] == "Placed"
    assert item is not None
    assert item["quantity"] == 2
    assert product["quantity"] == 18
    assert product["availability"] == "Available"


def test_consumer_order_history_and_details(client):
    farmer_id = create_user(
        "Integration Farmer",
        "farmer@example.com",
        "password123",
        "farmer",
    )

    consumer_id = create_user(
        "Integration Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
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
            farmer_id,
            "Order Product",
            "Vegetables",
            10,
            100,
            "Delhi",
            "Fresh",
            "Available",
        ),
    )

    product_id = cursor.lastrowid

    cursor = conn.execute(
        """
        INSERT INTO orders
        (buyer_id, total_amount, status)
        VALUES (?, ?, ?)
        """,
        (
            consumer_id,
            100,
            "Placed",
        ),
    )

    order_id = cursor.lastrowid

    conn.execute(
        """
        INSERT INTO order_items
        (
            order_id,
            product_id,
            seller_id,
            quantity,
            price,
            subtotal
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            order_id,
            product_id,
            farmer_id,
            1,
            100,
            100,
        ),
    )

    conn.commit()
    conn.close()

    login(
        client,
        "consumer@example.com",
        "password123",
    )

    response = client.get("/orders")

    assert response.status_code == 200

    response = client.get(
        f"/orders/{order_id}"
    )

    assert response.status_code == 200
    assert b"Order Product" in response.data


def test_bulk_requirement_to_offer_flow(client):
    buyer_id = create_user(
        "Integration Buyer",
        "buyer@example.com",
        "password123",
        "bulk_buyer",
    )

    seller_id = create_user(
        "Integration Seller",
        "seller@example.com",
        "password123",
        "farmer",
    )

    login(
        client,
        "buyer@example.com",
        "password123",
    )

    response = client.post(
        "/requirements/add",
        data={
            "product_name": "Integration Potato",
            "category": "Vegetables",
            "quantity": "500",
            "target_price": "20",
            "delivery_location": "Delhi",
            "delivery_date": "2026-12-01",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    conn = database.get_db_connection()

    requirement = conn.execute(
        """
        SELECT *
        FROM bulk_requirements
        WHERE buyer_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (buyer_id,),
    ).fetchone()

    conn.close()

    assert requirement is not None
    assert requirement["status"] == "Open"

    client.get("/logout")

    login(
        client,
        "seller@example.com",
        "password123",
    )

    response = client.post(
        f"/requirements/{requirement['id']}/offer",
        data={
            "quantity": "200",
            "price": "18",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    conn = database.get_db_connection()

    offer = conn.execute(
        """
        SELECT *
        FROM offers
        WHERE requirement_id = ?
        AND seller_id = ?
        """,
        (
            requirement["id"],
            seller_id,
        ),
    ).fetchone()

    conn.close()

    assert offer is not None
    assert offer["quantity"] == 200
    assert offer["price"] == 18
    assert offer["status"] == "Pending"


def test_bulk_buyer_can_accept_offer(client):
    buyer_id = create_user(
        "Integration Buyer",
        "buyer@example.com",
        "password123",
        "bulk_buyer",
    )

    seller_id = create_user(
        "Integration Seller",
        "seller@example.com",
        "password123",
        "farmer",
    )

    conn = database.get_db_connection()

    cursor = conn.execute(
        """
        INSERT INTO bulk_requirements
        (
            buyer_id,
            product_name,
            category,
            quantity,
            target_price,
            delivery_location,
            delivery_date,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            buyer_id,
            "Potato",
            "Vegetables",
            500,
            20,
            "Delhi",
            "2026-12-01",
            "Open",
        ),
    )

    requirement_id = cursor.lastrowid

    cursor = conn.execute(
        """
        INSERT INTO offers
        (
            requirement_id,
            seller_id,
            quantity,
            price,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            requirement_id,
            seller_id,
            200,
            18,
            "Pending",
        ),
    )

    offer_id = cursor.lastrowid

    conn.commit()
    conn.close()

    login(
        client,
        "buyer@example.com",
        "password123",
    )

    response = client.post(
        f"/offers/{offer_id}/Accepted",
        follow_redirects=True,
    )

    assert response.status_code == 200

    conn = database.get_db_connection()

    offer = conn.execute(
        """
        SELECT status
        FROM offers
        WHERE id = ?
        """,
        (offer_id,),
    ).fetchone()

    conn.close()

    assert offer["status"] == "Accepted"


def test_database_changes_are_reflected_in_application(client):
    farmer_id = create_user(
        "Integration Farmer",
        "farmer@example.com",
        "password123",
        "farmer",
    )

    create_product_name = "Database Visible Product"

    conn = database.get_db_connection()

    conn.execute(
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
            farmer_id,
            create_product_name,
            "Grains",
            50,
            30,
            "Delhi",
            "Fresh",
            "Available",
        ),
    )

    conn.commit()
    conn.close()

    create_user(
        "Integration Consumer",
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
        "/marketplace?search=Database+Visible+Product"
    )

    assert response.status_code == 200
    assert create_product_name.encode() in response.data


def test_invalid_order_is_rejected(client):
    create_user(
        "Integration Consumer",
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
        "/orders/place",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Your cart is empty." in response.data