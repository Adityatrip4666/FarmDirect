import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from werkzeug.security import generate_password_hash

import database
import app as farmdirect_app
from werkzeug.security import generate_password_hash

import database
import app as farmdirect_app


@pytest.fixture
def client(monkeypatch):
    # Create a temporary database for testing.
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)

    monkeypatch.setattr(database, "DATABASE", db_path)

    database.init_db()

    farmdirect_app.app.config["TESTING"] = True
    farmdirect_app.app.config["SECRET_KEY"] = "test-secret-key"

    with farmdirect_app.app.test_client() as client:
        yield client

    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except PermissionError:
            pass


def create_user(
    name,
    email,
    password,
    role,
    status="Active",
):
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


def create_product(
    seller_id,
    name="Rice",
    category="Grains",
    quantity=100,
    price=50,
    location="Delhi",
):
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
            seller_id,
            name,
            category,
            quantity,
            price,
            location,
            "Good quality",
            "Available",
        ),
    )

    product_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return product_id


def login(client, email, password):
    return client.post(
        "/login",
        data={
            "email": email,
            "password": password,
        },
        follow_redirects=True,
    )


# -------------------------
# Authentication tests
# -------------------------


def test_register_valid_user(client):
    response = client.post(
        "/register",
        data={
            "name": "Test Farmer",
            "email": "farmer@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "role": "farmer",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    conn = database.get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        ("farmer@example.com",),
    ).fetchone()

    conn.close()

    assert user is not None
    assert user["role"] == "farmer"


def test_login_valid_user(client):
    create_user(
        "Test Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    response = login(
        client,
        "consumer@example.com",
        "password123",
    )

    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_login_invalid_password(client):
    create_user(
        "Test Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    response = login(
        client,
        "consumer@example.com",
        "wrongpassword",
    )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_inactive_user_cannot_login(client):
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


# -------------------------
# Authorization tests
# -------------------------


def test_marketplace_requires_consumer_or_bulk_buyer(client):
    response = client.get("/marketplace")

    assert response.status_code in (302, 403)


def test_consumer_can_access_marketplace(client):
    create_user(
        "Test Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(client, "consumer@example.com", "password123")

    response = client.get("/marketplace")

    assert response.status_code == 200


def test_farmer_cannot_access_marketplace(client):
    create_user(
        "Test Farmer",
        "farmer@example.com",
        "password123",
        "farmer",
    )

    login(client, "farmer@example.com", "password123")

    response = client.get("/marketplace")

    assert response.status_code in (302, 403)


# -------------------------
# Product tests
# -------------------------


def test_farmer_can_add_product(client):
    farmer_id = create_user(
        "Test Farmer",
        "farmer@example.com",
        "password123",
        "farmer",
    )

    login(client, "farmer@example.com", "password123")

    response = client.post(
        "/products/add",
        data={
            "name": "Wheat",
            "category": "Grains",
            "quantity": "100",
            "price": "40",
            "location": "Delhi",
            "quality_details": "Fresh wheat",
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
        (farmer_id, "Wheat"),
    ).fetchone()

    conn.close()

    assert product is not None
    assert product["quantity"] == 100
    assert product["price"] == 40


def test_farmer_cannot_add_invalid_product(client):
    create_user(
        "Test Farmer",
        "farmer@example.com",
        "password123",
        "farmer",
    )

    login(client, "farmer@example.com", "password123")

    response = client.post(
        "/products/add",
        data={
            "name": "Wheat",
            "category": "Grains",
            "quantity": "-10",
            "price": "40",
            "location": "Delhi",
            "quality_details": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Quantity must be a positive number." in response.data


def test_consumer_cannot_add_product(client):
    create_user(
        "Test Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(client, "consumer@example.com", "password123")

    response = client.post(
        "/products/add",
        data={
            "name": "Wheat",
            "category": "Grains",
            "quantity": "100",
            "price": "40",
            "location": "Delhi",
        },
    )

    assert response.status_code in (302, 403)


# -------------------------
# Marketplace filtering
# -------------------------


def test_marketplace_search_finds_product(client):
    farmer_id = create_user(
        "Test Farmer",
        "farmer@example.com",
        "password123",
        "farmer",
    )

    create_product(
        farmer_id,
        name="Fresh Rice",
        category="Grains",
        quantity=100,
        price=50,
    )

    create_user(
        "Test Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(client, "consumer@example.com", "password123")

    response = client.get("/marketplace?search=Fresh+Rice")

    assert response.status_code == 200
    assert b"Fresh Rice" in response.data


# -------------------------
# Cart tests
# -------------------------


def test_consumer_can_add_product_to_cart(client):
    farmer_id = create_user(
        "Test Farmer",
        "farmer@example.com",
        "password123",
        "farmer",
    )

    product_id = create_product(
        farmer_id,
        name="Rice",
        quantity=20,
        price=50,
    )

    create_user(
        "Test Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(client, "consumer@example.com", "password123")

    response = client.post(
        f"/cart/add/{product_id}",
        data={"quantity": "2"},
        follow_redirects=True,
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert session["cart"][str(product_id)] == 2


def test_cart_rejects_invalid_quantity(client):
    farmer_id = create_user(
        "Test Farmer",
        "farmer@example.com",
        "password123",
        "farmer",
    )

    product_id = create_product(farmer_id)

    create_user(
        "Test Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(client, "consumer@example.com", "password123")

    response = client.post(
        f"/cart/add/{product_id}",
        data={"quantity": "-2"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Quantity must be a positive whole number." in response.data


def test_consumer_can_view_empty_cart(client):
    create_user(
        "Test Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(client, "consumer@example.com", "password123")

    response = client.get("/cart")

    assert response.status_code == 200


# -------------------------
# Bulk requirement tests
# -------------------------


def test_bulk_buyer_can_create_requirement(client):
    buyer_id = create_user(
        "Bulk Buyer",
        "buyer@example.com",
        "password123",
        "bulk_buyer",
    )

    response = login(
        client,
        "buyer@example.com",
        "password123",
    )

    assert response.status_code == 200

    response = client.post(
        "/requirements/add",
        data={
            "product_name": "Potato",
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
        """,
        (buyer_id,),
    ).fetchone()

    conn.close()

    assert requirement is not None
    assert requirement["status"] == "Open"


def test_bulk_requirement_rejects_invalid_quantity(client):
    create_user(
        "Bulk Buyer",
        "buyer@example.com",
        "password123",
        "bulk_buyer",
    )

    login(client, "buyer@example.com", "password123")

    response = client.post(
        "/requirements/add",
        data={
            "product_name": "Potato",
            "category": "Vegetables",
            "quantity": "-100",
            "target_price": "20",
            "delivery_location": "Delhi",
            "delivery_date": "2026-12-01",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Quantity must be greater than 0." in response.data


# -------------------------
# Bulk offer tests
# -------------------------


def test_farmer_can_submit_offer(client):
    buyer_id = create_user(
        "Bulk Buyer",
        "buyer@example.com",
        "password123",
        "bulk_buyer",
    )

    farmer_id = create_user(
        "Test Farmer",
        "farmer@example.com",
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

    conn.commit()
    conn.close()

    login(client, "farmer@example.com", "password123")

    response = client.post(
        f"/requirements/{requirement_id}/offer",
        data={
            "quantity": "100",
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
        (requirement_id, farmer_id),
    ).fetchone()

    conn.close()

    assert offer is not None
    assert offer["status"] == "Pending"


def test_offer_rejects_excess_quantity(client):
    buyer_id = create_user(
        "Bulk Buyer",
        "buyer@example.com",
        "password123",
        "bulk_buyer",
    )

    create_user(
        "Test Farmer",
        "farmer@example.com",
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
            100,
            20,
            "Delhi",
            "2026-12-01",
            "Open",
        ),
    )

    requirement_id = cursor.lastrowid

    conn.commit()
    conn.close()

    login(client, "farmer@example.com", "password123")

    response = client.post(
        f"/requirements/{requirement_id}/offer",
        data={
            "quantity": "200",
            "price": "18",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Offer quantity cannot exceed the required quantity." in response.data


# -------------------------
# Admin tests
# -------------------------


def test_admin_can_access_dashboard(client):
    create_user(
        "Admin User",
        "admin@example.com",
        "password123",
        "admin",
    )

    login(client, "admin@example.com", "password123")

    response = client.get("/admin/dashboard")

    assert response.status_code == 200


def test_non_admin_cannot_access_admin_dashboard(client):
    create_user(
        "Test Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(client, "consumer@example.com", "password123")

    response = client.get("/admin/dashboard")

    assert response.status_code in (302, 403)


def test_admin_can_view_users(client):
    create_user(
        "Admin User",
        "admin@example.com",
        "password123",
        "admin",
    )

    login(client, "admin@example.com", "password123")

    response = client.get("/admin/users")

    assert response.status_code == 200


def test_admin_can_deactivate_user(client):
    create_user(
        "Admin User",
        "admin@example.com",
        "password123",
        "admin",
    )

    user_id = create_user(
        "Test Consumer",
        "consumer@example.com",
        "password123",
        "consumer",
    )

    login(client, "admin@example.com", "password123")

    response = client.post(
        f"/admin/users/{user_id}/deactivate",
        follow_redirects=True,
    )

    assert response.status_code == 200

    conn = database.get_db_connection()

    user = conn.execute(
        "SELECT status FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()

    conn.close()

    assert user["status"] == "Inactive"


def test_consumer_can_review_purchased_product(client):
    from werkzeug.security import generate_password_hash

    conn = database.get_db_connection()

    seller_cursor = conn.execute(
        """
        INSERT INTO users
        (name, email, password_hash, role, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Farmer",
            "review_farmer@example.com",
            generate_password_hash("password123"),
            "farmer",
            "Active",
        ),
    )

    seller_id = seller_cursor.lastrowid

    buyer_cursor = conn.execute(
        """
        INSERT INTO users
        (name, email, password_hash, role, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Consumer",
            "review_consumer@example.com",
            generate_password_hash("password123"),
            "consumer",
            "Active",
        ),
    )

    buyer_id = buyer_cursor.lastrowid

    product_cursor = conn.execute(
        """
        INSERT INTO products
        (
            seller_id,
            name,
            category,
            quantity,
            price,
            location,
            availability
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            seller_id,
            "Test Tomatoes",
            "Vegetables",
            10,
            50,
            "Delhi",
            "Available",
        ),
    )

    product_id = product_cursor.lastrowid

    order_cursor = conn.execute(
        """
        INSERT INTO orders
        (buyer_id, total_amount, status)
        VALUES (?, ?, ?)
        """,
        (
            buyer_id,
            50,
            "Pending",
        ),
    )

    order_id = order_cursor.lastrowid

    conn.execute(
        """
    INSERT INTO order_items
    (order_id, product_id, seller_id, quantity, price, subtotal)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            order_id,
            product_id,
            seller_id,
            1,
            50,
            50,
        ),
    )
    conn.commit()
    conn.close()

    response = client.post(
        "/login",
        data={
            "email": "review_consumer@example.com",
            "password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    response = client.post(
        f"/products/{product_id}/reviews/add",
        data={
            "rating": "5",
            "review_text": "Excellent quality product.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Review submitted successfully." in response.data

    conn = database.get_db_connection()

    review = conn.execute(
        """
        SELECT *
        FROM reviews
        WHERE reviewer_id = ?
          AND product_id = ?
          AND order_id = ?
        """,
        (
            buyer_id,
            product_id,
            order_id,
        ),
    ).fetchone()

    conn.close()

    assert review is not None
    assert review["rating"] == 5
    assert review["review_text"] == "Excellent quality product."


def test_consumer_cannot_review_unpurchased_product(client):
    from werkzeug.security import generate_password_hash

    conn = database.get_db_connection()

    seller_cursor = conn.execute(
        """
        INSERT INTO users
        (name, email, password_hash, role, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Farmer",
            "review_seller@example.com",
            generate_password_hash("password123"),
            "farmer",
            "Active",
        ),
    )

    seller_id = seller_cursor.lastrowid

    conn.execute(
        """
        INSERT INTO users
        (name, email, password_hash, role, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Consumer",
            "review_buyer@example.com",
            generate_password_hash("password123"),
            "consumer",
            "Active",
        ),
    )

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
            availability
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            seller_id,
            "Unpurchased Product",
            "Vegetables",
            10,
            50,
            "Delhi",
            "Available",
        ),
    )

    conn.commit()
    conn.close()

    client.post(
        "/login",
        data={
            "email": "review_buyer@example.com",
            "password": "password123",
        },
    )

    conn = database.get_db_connection()

    product = conn.execute(
        """
        SELECT id
        FROM products
        WHERE name = ?
        """,
        ("Unpurchased Product",),
    ).fetchone()

    conn.close()

    response = client.post(
        f"/products/{product['id']}/reviews/add",
        data={
            "rating": "5",
            "review_text": "This should not be accepted.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"You can only review products you have purchased." in response.data


def test_review_rejects_invalid_rating(client):
    from werkzeug.security import generate_password_hash

    conn = database.get_db_connection()

    conn.execute(
        """
        INSERT INTO users
        (name, email, password_hash, role, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Consumer",
            "invalid_rating@example.com",
            generate_password_hash("password123"),
            "consumer",
            "Active",
        ),
    )

    conn.commit()
    conn.close()

    client.post(
        "/login",
        data={
            "email": "invalid_rating@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/products/999999/reviews/add",
        data={
            "rating": "6",
            "review_text": "Invalid rating.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Rating must be between 1 and 5." in response.data


def test_duplicate_review_is_rejected(client):
    from werkzeug.security import generate_password_hash

    conn = database.get_db_connection()

    seller_cursor = conn.execute(
        """
        INSERT INTO users
        (name, email, password_hash, role, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Farmer",
            "duplicate_farmer@example.com",
            generate_password_hash("password123"),
            "farmer",
            "Active",
        ),
    )

    seller_id = seller_cursor.lastrowid

    buyer_cursor = conn.execute(
        """
        INSERT INTO users
        (name, email, password_hash, role, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Consumer",
            "duplicate_buyer@example.com",
            generate_password_hash("password123"),
            "consumer",
            "Active",
        ),
    )

    buyer_id = buyer_cursor.lastrowid

    product_cursor = conn.execute(
        """
        INSERT INTO products
        (
            seller_id,
            name,
            category,
            quantity,
            price,
            location,
            availability
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            seller_id,
            "Duplicate Test Product",
            "Vegetables",
            10,
            50,
            "Delhi",
            "Available",
        ),
    )

    product_id = product_cursor.lastrowid

    order_cursor = conn.execute(
        """
        INSERT INTO orders
        (buyer_id, total_amount, status)
        VALUES (?, ?, ?)
        """,
        (
            buyer_id,
            50,
            "Pending",
        ),
    )

    order_id = order_cursor.lastrowid

    conn.execute(
        """
        INSERT INTO order_items
        (order_id, product_id, seller_id, quantity, price, subtotal)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            order_id,
            product_id,
            seller_id,
            1,
            50,
            50,
        ),
    )

    conn.commit()
    conn.close()

    client.post(
        "/login",
        data={
            "email": "duplicate_buyer@example.com",
            "password": "password123",
        },
    )

    first_response = client.post(
        f"/products/{product_id}/reviews/add",
        data={
            "rating": "5",
            "review_text": "First review.",
        },
        follow_redirects=True,
    )

    assert first_response.status_code == 200

    second_response = client.post(
        f"/products/{product_id}/reviews/add",
        data={
            "rating": "4",
            "review_text": "Second review.",
        },
        follow_redirects=True,
    )

    assert second_response.status_code == 200
    assert b"You have already reviewed this purchase." in second_response.data


def test_product_reviews_display_average_rating(client):
    from werkzeug.security import generate_password_hash

    conn = database.get_db_connection()

    seller_cursor = conn.execute(
        """
        INSERT INTO users
        (name, email, password_hash, role, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Farmer",
            "rating_farmer@example.com",
            generate_password_hash("password123"),
            "farmer",
            "Active",
        ),
    )

    seller_id = seller_cursor.lastrowid

    buyer_cursor = conn.execute(
        """
        INSERT INTO users
        (name, email, password_hash, role, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "Consumer",
            "rating_buyer@example.com",
            generate_password_hash("password123"),
            "consumer",
            "Active",
        ),
    )

    buyer_id = buyer_cursor.lastrowid

    product_cursor = conn.execute(
        """
        INSERT INTO products
        (
            seller_id,
            name,
            category,
            quantity,
            price,
            location,
            availability
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            seller_id,
            "Rated Product",
            "Fruits",
            10,
            100,
            "Delhi",
            "Available",
        ),
    )

    product_id = product_cursor.lastrowid

    order_cursor = conn.execute(
        """
        INSERT INTO orders
        (buyer_id, total_amount, status)
        VALUES (?, ?, ?)
        """,
        (
            buyer_id,
            100,
            "Pending",
        ),
    )

    order_id = order_cursor.lastrowid

    conn.execute(
        """
        INSERT INTO order_items
        (order_id, product_id, seller_id, quantity, price, subtotal)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (order_id, product_id, seller_id, 1, 50, 50),
    )

    conn.execute(
        """
        INSERT INTO reviews
        (
            reviewer_id,
            product_id,
            order_id,
            rating,
            review_text
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            buyer_id,
            product_id,
            order_id,
            4,
            "Good product.",
        ),
    )

    conn.commit()
    conn.close()

    client.post(
        "/login",
        data={
            "email": "rating_buyer@example.com",
            "password": "password123",
        },
    )

    response = client.get(f"/products/{product_id}/reviews")

    assert response.status_code == 200
    assert b"Average Rating:" in response.data
    assert b"4.0 / 5" in response.data
    assert b"Good product." in response.data
