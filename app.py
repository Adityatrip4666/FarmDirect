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
