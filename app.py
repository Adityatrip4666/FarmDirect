from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, init_db
import os
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to access this page.", "error")
                return redirect(url_for("login"))

            if session.get("role") not in allowed_roles:
                flash("You are not authorized to access this page.", "error")
                return redirect(url_for("dashboard"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def get_cart():
    return session.get("cart", {})


app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")

VALID_ROLES = ["farmer", "fpo", "consumer", "bulk_buyer"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "").strip()

        # Required field validation
        if not name or not email or not password or not confirm_password or not role:
            flash("All fields are required.", "error")
            return render_template("register.html")

        # Role validation
        if role not in VALID_ROLES:
            flash("Invalid role selected.", "error")
            return render_template("register.html")

        # Password confirmation
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        # Password length validation
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")

        conn = get_db_connection()

        # Duplicate account check
        existing_user = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()

        if existing_user:
            conn.close()
            flash("An account with this email already exists.", "error")
            return render_template("register.html")

        # Secure password hashing
        password_hash = generate_password_hash(password)

        conn.execute(
            """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, password_hash, role),
        )

        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        conn = get_db_connection()

        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        conn.close()

        # Invalid credentials
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        # Clear old session and create new authenticated session
        session.clear()

        session["user_id"] = user["id"]
        session["name"] = user["name"]
        session["role"] = user["role"]

        flash(f"Welcome back, {user['name']}!", "success")

        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    role = session.get("role")

    if role == "farmer":
        return redirect(url_for("farmer_dashboard"))

    elif role == "fpo":
        return redirect(url_for("fpo_dashboard"))

    elif role == "consumer":
        return redirect(url_for("consumer_dashboard"))

    elif role == "bulk_buyer":
        return redirect(url_for("bulk_buyer_dashboard"))

    elif role == "admin":
        return redirect(url_for("admin_dashboard"))

    else:
        flash("Unknown role.", "error")
        return redirect(url_for("logout"))


@app.route("/farmer/dashboard")
@role_required("farmer")
def farmer_dashboard():
    return render_template("role_dashboard.html", role_label="Farmer")


@app.route("/fpo/dashboard")
@role_required("fpo")
def fpo_dashboard():
    return render_template("role_dashboard.html", role_label="FPO")


@app.route("/consumer/dashboard")
@role_required("consumer")
def consumer_dashboard():
    return render_template("role_dashboard.html", role_label="Consumer")


@app.route("/bulk-buyer/dashboard")
@role_required("bulk_buyer")
def bulk_buyer_dashboard():
    return render_template("role_dashboard.html", role_label="Bulk Buyer")


@app.route("/admin/dashboard")
@role_required("admin")
def admin_dashboard():
    conn = get_db_connection()

    users = conn.execute(
        """
        SELECT id, name, email, role, created_at
        FROM users
        """
    ).fetchall()

    conn.close()

    return render_template("admin_dashboard.html", users=users)


@app.route("/user/<int:user_id>/account")
@login_required
def view_account(user_id):

    # Users can only access their own account.
    # Admin can access any user's account.
    if session.get("user_id") != user_id and session.get("role") != "admin":
        flash("You cannot access another user's account.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()

    user = conn.execute(
        """
        SELECT id, name, email, role
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    conn.close()

    if user is None:
        flash("User not found.", "error")
        return redirect(url_for("dashboard"))

    return render_template("account.html", user=user)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    role = session.get("role")

    if role not in ["farmer", "fpo"]:
        flash("Only farmers and FPOs can manage profiles.", "error")
        return redirect(url_for("dashboard"))

    table = "farmer_profiles" if role == "farmer" else "fpo_profiles"

    conn = get_db_connection()

    profile_data = conn.execute(
        f"SELECT * FROM {table} WHERE user_id = ?", (user_id,)
    ).fetchone()

    if request.method == "POST":
        location = request.form.get("location", "").strip()
        phone = request.form.get("phone", "").strip()
        description = request.form.get("description", "").strip()

        if not location or not phone:
            conn.close()
            flash("Location and phone are required.", "error")
            return render_template("profile.html", user=session, profile=profile_data)

        if profile_data:
            conn.execute(
                f"""
                UPDATE {table}
                SET location = ?, phone = ?, description = ?
                WHERE user_id = ?
                """,
                (location, phone, description, user_id),
            )
            message = "Profile updated successfully."
        else:
            conn.execute(
                f"""
                INSERT INTO {table}
                (user_id, location, phone, description)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, location, phone, description),
            )
            message = "Profile created successfully."

        conn.commit()

        profile_data = conn.execute(
            f"SELECT * FROM {table} WHERE user_id = ?", (user_id,)
        ).fetchone()

        flash(message, "success")

    conn.close()

    return render_template("profile.html", user=session, profile=profile_data)


@app.route("/seller/<int:user_id>/profile")
@login_required
def seller_profile(user_id):
    # Only consumers and bulk buyers can view seller profiles
    if session.get("role") not in ["consumer", "bulk_buyer"]:
        flash("Only authorized buyers can view seller profiles.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()

    # Get only Farmer or FPO
    user = conn.execute(
        """
        SELECT id, name, email, role
        FROM users
        WHERE id = ? AND role IN ('farmer', 'fpo')
        """,
        (user_id,),
    ).fetchone()

    if user is None:
        conn.close()
        flash("Seller profile not found.", "error")
        return redirect(url_for("dashboard"))

    # Get the appropriate profile
    if user["role"] == "farmer":
        profile = conn.execute(
            """
            SELECT location, phone, description
            FROM farmer_profiles
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
    else:
        profile = conn.execute(
            """
            SELECT location, phone, description
            FROM fpo_profiles
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    conn.close()

    # Seller exists but has no profile
    if profile is None:
        flash("This seller has not created a profile yet.", "error")
        return redirect(url_for("dashboard"))

    return render_template("seller_profile.html", user=user, profile=profile)


@app.route("/marketplace")
@role_required("consumer", "bulk_buyer")
def marketplace():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    max_price = request.args.get("max_price", "").strip()
    location = request.args.get("location", "").strip()

    query = """
        SELECT products.*, users.name AS seller_name, users.role AS seller_role
        FROM products
        JOIN users ON products.seller_id = users.id
        WHERE products.availability = 'Available'
    """

    params = []

    if search:
        query += " AND products.name LIKE ?"
        params.append(f"%{search}%")

    if category:
        query += " AND products.category = ?"
        params.append(category)

    if max_price:
        try:
            max_price_value = float(max_price)

            if max_price_value < 0:
                raise ValueError

            query += " AND products.price <= ?"
            params.append(max_price_value)

        except ValueError:
            flash("Maximum price must be a valid positive number.", "error")
            max_price = ""

    if location:
        query += " AND products.location LIKE ?"
        params.append(f"%{location}%")

    query += " ORDER BY products.created_at DESC"

    conn = get_db_connection()
    products = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "marketplace.html",
        products=products,
        search=search,
        category=category,
        max_price=max_price,
        location=location,
    )


@app.route("/cart/add/<int:product_id>", methods=["POST"])
@role_required("consumer")
def add_to_cart(product_id):
    quantity = request.form.get("quantity", "1").strip()

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        flash("Quantity must be a positive whole number.", "error")
        return redirect(url_for("marketplace"))

    conn = get_db_connection()

    product = conn.execute(
        """
        SELECT id, name, quantity, price, availability
        FROM products
        WHERE id = ? AND availability = 'Available'
        """,
        (product_id,),
    ).fetchone()

    conn.close()

    if product is None:
        flash("Product is not available.", "error")
        return redirect(url_for("marketplace"))

    cart = get_cart()

    current_quantity = int(cart.get(str(product_id), 0))
    new_quantity = current_quantity + quantity

    if new_quantity > product["quantity"]:
        flash(
            f"Only {product['quantity']} units of {product['name']} are available.",
            "error",
        )
        return redirect(url_for("marketplace"))

    cart[str(product_id)] = new_quantity
    session["cart"] = cart
    session.modified = True

    flash("Product added to cart.", "success")
    return redirect(url_for("marketplace"))


@app.route("/cart")
@role_required("consumer")
def cart():
    cart = get_cart()

    if not cart:
        return render_template("cart.html", cart_items=[], total=0)

    product_ids = list(cart.keys())

    placeholders = ",".join("?" for _ in product_ids)

    conn = get_db_connection()

    products = conn.execute(
        f"""
        SELECT id, name, category, quantity, price, location
        FROM products
        WHERE id IN ({placeholders})
        """,
        product_ids,
    ).fetchall()

    conn.close()

    cart_items = []
    total = 0

    for product in products:
        quantity = int(cart.get(str(product["id"]), 0))
        subtotal = quantity * product["price"]
        total += subtotal

        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    return render_template("cart.html", cart_items=cart_items, total=total)


@app.route("/orders/place", methods=["POST"])
@role_required("consumer")
def place_order():
    cart = get_cart()

    if not cart:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart"))

    conn = get_db_connection()

    try:
        product_ids = list(cart.keys())
        placeholders = ",".join("?" for _ in product_ids)

        products = conn.execute(
            f"""
            SELECT id, name, seller_id, quantity, price, availability
            FROM products
            WHERE id IN ({placeholders})
            """,
            product_ids,
        ).fetchall()

        if len(products) != len(product_ids):
            conn.rollback()
            flash("One or more products are no longer available.", "error")
            return redirect(url_for("cart"))

        total_amount = 0
        order_items = []

        for product in products:
            requested_quantity = int(cart[str(product["id"])])

            if requested_quantity <= 0:
                conn.rollback()
                flash("Invalid product quantity.", "error")
                return redirect(url_for("cart"))

            if product["availability"] != "Available":
                conn.rollback()
                flash(f"{product['name']} is no longer available.", "error")
                return redirect(url_for("cart"))

            if requested_quantity > product["quantity"]:
                conn.rollback()
                flash(
                    f"Only {product['quantity']} units of "
                    f"{product['name']} are available.",
                    "error",
                )
                return redirect(url_for("cart"))

            subtotal = requested_quantity * product["price"]
            total_amount += subtotal

            order_items.append(
                (
                    product["id"],
                    product["seller_id"],
                    requested_quantity,
                    product["price"],
                    subtotal,
                )
            )

        cursor = conn.execute(
            """
            INSERT INTO orders (buyer_id, total_amount, status)
            VALUES (?, ?, ?)
            """,
            (
                session["user_id"],
                total_amount,
                "Placed",
            ),
        )

        order_id = cursor.lastrowid

        for product_id, seller_id, quantity, price, subtotal in order_items:
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
                    quantity,
                    price,
                    subtotal,
                ),
            )

            conn.execute(
                """
                UPDATE products
                SET quantity = quantity - ?,
                    availability = CASE
                        WHEN quantity - ? <= 0 THEN 'Unavailable'
                        ELSE 'Available'
                    END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    quantity,
                    quantity,
                    product_id,
                ),
            )

        conn.commit()

        session["cart"] = {}
        session.modified = True

        flash(f"Order #{order_id} placed successfully.", "success")

        return redirect(url_for("order_history"))

    except Exception:
        conn.rollback()
        flash("Unable to place the order. Please try again.", "error")
        return redirect(url_for("cart"))

    finally:
        conn.close()


@app.route("/orders")
@role_required("consumer")
def order_history():
    conn = get_db_connection()

    orders = conn.execute(
        """
        SELECT id, total_amount, status, created_at
        FROM orders
        WHERE buyer_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],),
    ).fetchall()

    conn.close()

    return render_template("orders.html", orders=orders)


@app.route("/orders/<int:order_id>")
@role_required("consumer")
def order_details(order_id):
    conn = get_db_connection()

    order = conn.execute(
        """
        SELECT id, total_amount, status, created_at
        FROM orders
        WHERE id = ? AND buyer_id = ?
        """,
        (
            order_id,
            session["user_id"],
        ),
    ).fetchone()

    if order is None:
        conn.close()
        flash("Order not found or you are not authorized to view it.", "error")
        return redirect(url_for("order_history"))

    items = conn.execute(
        """
        SELECT
            order_items.quantity,
            order_items.price,
            order_items.subtotal,
            products.name
        FROM order_items
        JOIN products
            ON order_items.product_id = products.id
        WHERE order_items.order_id = ?
        """,
        (order_id,),
    ).fetchall()

    conn.close()

    return render_template("order_details.html", order=order, items=items)


@app.route("/requirements/add", methods=["GET", "POST"])
@role_required("bulk_buyer")
def add_requirement():
    if request.method == "POST":
        product_name = request.form.get("product_name", "").strip()
        category = request.form.get("category", "").strip()
        quantity = request.form.get("quantity", "").strip()
        target_price = request.form.get("target_price", "").strip()
        delivery_location = request.form.get("delivery_location", "").strip()
        delivery_date = request.form.get("delivery_date", "").strip()

        if not product_name or not category:
            flash("Product name and category are required.", "error")
            return render_template("add_requirement.html")

        if not delivery_location or not delivery_date:
            flash("Delivery location and date are required.", "error")
            return render_template("add_requirement.html")

        try:
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            flash("Quantity must be greater than 0.", "error")
            return render_template("add_requirement.html")

        try:
            target_price = float(target_price)
            if target_price <= 0:
                raise ValueError
        except ValueError:
            flash("Target price must be greater than 0.", "error")
            return render_template("add_requirement.html")

        conn = get_db_connection()

        conn.execute(
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
                session["user_id"],
                product_name,
                category,
                quantity,
                target_price,
                delivery_location,
                delivery_date,
                "Open",
            ),
        )

        conn.commit()
        conn.close()

        flash("Bulk requirement created successfully.", "success")
        return redirect(url_for("my_requirements"))

    return render_template("add_requirement.html")


@app.route("/requirements")
@role_required("bulk_buyer")
def my_requirements():
    conn = get_db_connection()

    requirements = conn.execute(
        """
        SELECT
            id,
            product_name,
            category,
            quantity,
            target_price,
            delivery_location,
            delivery_date,
            status,
            created_at
        FROM bulk_requirements
        WHERE buyer_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],),
    ).fetchall()

    conn.close()

    return render_template("requirements.html", requirements=requirements)


@app.route("/requirements/available")
@role_required("farmer", "fpo")
def available_requirements():
    conn = get_db_connection()

    requirements = conn.execute(
        """
        SELECT
            bulk_requirements.id,
            bulk_requirements.product_name,
            bulk_requirements.category,
            bulk_requirements.quantity,
            bulk_requirements.target_price,
            bulk_requirements.delivery_location,
            bulk_requirements.delivery_date,
            bulk_requirements.status,
            users.name AS buyer_name
        FROM bulk_requirements
        JOIN users
            ON bulk_requirements.buyer_id = users.id
        WHERE bulk_requirements.status = 'Open'
        ORDER BY bulk_requirements.created_at DESC
        """
    ).fetchall()

    conn.close()

    return render_template("available_requirements.html", requirements=requirements)


@app.route("/requirements/<int:requirement_id>/offers")
@role_required("bulk_buyer")
def requirement_offers(requirement_id):
    conn = get_db_connection()

    requirement = conn.execute(
        """
        SELECT
            id,
            product_name,
            category,
            quantity,
            target_price,
            delivery_location,
            delivery_date,
            status
        FROM bulk_requirements
        WHERE id = ? AND buyer_id = ?
        """,
        (requirement_id, session["user_id"]),
    ).fetchone()

    if requirement is None:
        conn.close()
        flash("Requirement not found or you are not authorized to view it.", "error")
        return redirect(url_for("my_requirements"))

    offers = conn.execute(
        """
        SELECT
            offers.id,
            offers.quantity,
            offers.price,
            offers.status,
            offers.created_at,
            users.name AS seller_name,
            users.role AS seller_role
        FROM offers
        JOIN users
            ON offers.seller_id = users.id
        WHERE offers.requirement_id = ?
        ORDER BY offers.created_at DESC
        """,
        (requirement_id,),
    ).fetchall()

    conn.close()

    return render_template("offers.html", requirement=requirement, offers=offers)


@app.route("/offers/<int:offer_id>/<status>", methods=["POST"])
@role_required("bulk_buyer")
def update_offer_status(offer_id, status):

    if status not in ("Accepted", "Rejected"):
        flash("Invalid offer status.", "error")
        return redirect(url_for("my_requirements"))

    conn = get_db_connection()

    offer = conn.execute(
        """
        SELECT
            offers.id,
            offers.requirement_id
        FROM offers
        JOIN bulk_requirements
            ON offers.requirement_id = bulk_requirements.id
        WHERE offers.id = ?
        AND bulk_requirements.buyer_id = ?
        """,
        (offer_id, session["user_id"]),
    ).fetchone()

    if offer is None:
        conn.close()
        flash("Offer not found or you are not authorized.", "error")
        return redirect(url_for("my_requirements"))

    conn.execute(
        """
        UPDATE offers
        SET status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (status, offer_id),
    )

    conn.commit()
    conn.close()

    flash(f"Offer {status.lower()} successfully.", "success")

    return redirect(
        url_for("requirement_offers", requirement_id=offer["requirement_id"])
    )


@app.route("/requirements/<int:requirement_id>/offer", methods=["GET", "POST"])
@role_required("farmer", "fpo")
def submit_offer(requirement_id):
    conn = get_db_connection()

    requirement = conn.execute(
        """
        SELECT
            id,
            product_name,
            category,
            quantity,
            target_price,
            delivery_location,
            delivery_date,
            status
        FROM bulk_requirements
        WHERE id = ? AND status = 'Open'
        """,
        (requirement_id,),
    ).fetchone()

    if requirement is None:
        conn.close()
        flash("Requirement not found or no longer open.", "error")
        return redirect(url_for("available_requirements"))

    if request.method == "POST":
        quantity = request.form.get("quantity", "").strip()
        price = request.form.get("price", "").strip()

        try:
            quantity = float(quantity)

            if quantity <= 0:
                raise ValueError
        except ValueError:
            conn.close()
            flash("Offer quantity must be greater than 0.", "error")
            return render_template("submit_offer.html", requirement=requirement)

        try:
            price = float(price)

            if price <= 0:
                raise ValueError
        except ValueError:
            conn.close()
            flash("Offer price must be greater than 0.", "error")
            return render_template("submit_offer.html", requirement=requirement)

        if quantity > requirement["quantity"]:
            conn.close()
            flash("Offer quantity cannot exceed the required quantity.", "error")
            return render_template("submit_offer.html", requirement=requirement)

        conn.execute(
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
                session["user_id"],
                quantity,
                price,
                "Pending",
            ),
        )

        conn.commit()
        conn.close()

        flash("Offer submitted successfully.", "success")
        return redirect(url_for("available_requirements"))

    conn.close()

    return render_template("submit_offer.html", requirement=requirement)


@app.route("/cart/update/<int:product_id>", methods=["POST"])
@role_required("consumer")
def update_cart(product_id):
    quantity = request.form.get("quantity", "").strip()

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        flash("Quantity must be a positive whole number.", "error")
        return redirect(url_for("cart"))

    conn = get_db_connection()

    product = conn.execute(
        """
        SELECT id, name, quantity, price, availability
        FROM products
        WHERE id = ?
        """,
        (product_id,),
    ).fetchone()

    conn.close()

    if product is None or product["availability"] != "Available":
        flash("Product is no longer available.", "error")
        return redirect(url_for("cart"))

    if quantity > product["quantity"]:
        flash(
            f"Only {product['quantity']} units of {product['name']} are available.",
            "error",
        )
        return redirect(url_for("cart"))

    cart = get_cart()
    cart[str(product_id)] = quantity
    session["cart"] = cart
    session.modified = True

    flash("Cart updated successfully.", "success")
    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:product_id>", methods=["POST"])
@role_required("consumer")
def remove_from_cart(product_id):
    cart = get_cart()

    cart.pop(str(product_id), None)

    session["cart"] = cart
    session.modified = True

    flash("Product removed from cart.", "success")
    return redirect(url_for("cart"))


@app.route("/cart/clear", methods=["POST"])
@role_required("consumer")
def clear_cart():
    session["cart"] = {}
    session.modified = True

    flash("Cart cleared.", "success")
    return redirect(url_for("cart"))


@app.route("/products/add", methods=["GET", "POST"])
@role_required("farmer", "fpo")
def add_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        quantity = request.form.get("quantity", "").strip()
        price = request.form.get("price", "").strip()
        location = request.form.get("location", "").strip()
        quality_details = request.form.get("quality_details", "").strip()

        # Required field validation
        if not name or not category or not quantity or not price or not location:
            flash(
                "Product name, category, quantity, price, and location are required.",
                "error",
            )
            return render_template("add_product.html")

        # Quantity validation
        try:
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            flash("Quantity must be a positive number.", "error")
            return render_template("add_product.html")

        # Price validation
        try:
            price = float(price)
            if price <= 0:
                raise ValueError
        except ValueError:
            flash("Price must be a positive number.", "error")
            return render_template("add_product.html")

        conn = get_db_connection()

        conn.execute(
            """
            INSERT INTO products
            (seller_id, name, category, quantity, price, location, quality_details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                name,
                category,
                quantity,
                price,
                location,
                quality_details,
            ),
        )

        conn.commit()
        conn.close()

        flash("Product added successfully.", "success")
        return redirect(url_for("my_products"))

    return render_template("add_product.html")


@app.route("/products")
@role_required("farmer", "fpo")
def my_products():
    conn = get_db_connection()

    products = conn.execute(
        """
        SELECT *
        FROM products
        WHERE seller_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],),
    ).fetchall()

    conn.close()

    return render_template("my_products.html", products=products)


@app.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
@role_required("farmer", "fpo")
def edit_product(product_id):
    conn = get_db_connection()

    product = conn.execute(
        """
        SELECT *
        FROM products
        WHERE id = ? AND seller_id = ?
        """,
        (product_id, session["user_id"]),
    ).fetchone()

    if product is None:
        conn.close()
        flash("Product not found or you are not authorized to edit it.", "error")
        return redirect(url_for("my_products"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        quantity = request.form.get("quantity", "").strip()
        price = request.form.get("price", "").strip()
        location = request.form.get("location", "").strip()
        quality_details = request.form.get("quality_details", "").strip()
        availability = request.form.get("availability", "").strip()

        # Required field validation
        if not name or not category or not quantity or not price or not location:
            conn.close()
            flash(
                "Product name, category, quantity, price, and location are required.",
                "error",
            )
            return render_template("edit_product.html", product=product)

        # Quantity validation
        try:
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            conn.close()
            flash("Quantity must be a positive number.", "error")
            return render_template("edit_product.html", product=product)

        # Price validation
        try:
            price = float(price)
            if price <= 0:
                raise ValueError
        except ValueError:
            conn.close()
            flash("Price must be a positive number.", "error")
            return render_template("edit_product.html", product=product)

        if availability not in ["Available", "Unavailable"]:
            availability = "Available"

        conn.execute(
            """
            UPDATE products
            SET name = ?,
                category = ?,
                quantity = ?,
                price = ?,
                location = ?,
                quality_details = ?,
                availability = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND seller_id = ?
            """,
            (
                name,
                category,
                quantity,
                price,
                location,
                quality_details,
                availability,
                product_id,
                session["user_id"],
            ),
        )

        conn.commit()
        conn.close()

        flash("Product updated successfully.", "success")
        return redirect(url_for("my_products"))

    conn.close()

    return render_template("edit_product.html", product=product)


@app.route("/products/delete/<int:product_id>", methods=["POST"])
@role_required("farmer", "fpo")
def delete_product(product_id):
    conn = get_db_connection()

    product = conn.execute(
        """
        SELECT id
        FROM products
        WHERE id = ? AND seller_id = ?
        """,
        (product_id, session["user_id"]),
    ).fetchone()

    if product is None:
        conn.close()
        flash("Product not found or you are not authorized to delete it.", "error")
        return redirect(url_for("my_products"))

    conn.execute(
        """
        DELETE FROM products
        WHERE id = ? AND seller_id = ?
        """,
        (product_id, session["user_id"]),
    )

    conn.commit()
    conn.close()

    flash("Product deleted successfully.", "success")
    return redirect(url_for("my_products"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
