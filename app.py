import random
from urllib.parse import urlparse
from utils.decorators import admin_required, login_required
import bcrypt
import flask_session
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from database import session as db_session
from models import Product, User, Log
from flask import session as cart_session

from utils.logger import log_action
from utils.security import hash_password, check_password

from services.ai_service import generate_text

app = Flask(__name__)
app.secret_key="fc0fa068be0f"

categories = ["Phone","Laptop","Monitor","Mouse","Keyboard","Audio device"]

def get_cart():
    print(cart_session)
    print(cart_session.items())
    if "cart" not in cart_session:
        cart_session["cart"] = {}
    return cart_session["cart"]

@app.route('/')
def home():
    products = db_session.query(Product).all()

    recommended = random.sample(products, min(len(products), 10)) if products else []

    return render_template('home.html', recommended=recommended)

@app.route('/catalogue')
def catalogue():
    q = (request.args.get("q") or "").strip()
    category = (request.args.get("category") or "").strip()
    page = int(request.args.get("page") or 1)
    per_page = 12
    max_price_raw = request.args.get("price") or "9999"

    try:
        max_price = int(max_price_raw)
    except ValueError:
        max_price = 9999

    query = db_session.query(Product)

    if q:
        like = f"%{q}%"
        query=query.filter(
            or_(
                Product.name.ilike(like)
            )
        )

    if category:
        query = query.filter(Product.category == category)

    query = query.filter(Product.price <= max_price)

    total_products = query.count()
    products = query.order_by(Product.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total_products + per_page - 1) // per_page
    db_session.close()

    return render_template('catalogue.html', categories=categories, q=q,category=category, products=products, page=page, total_pages=total_pages)

@app.route('/products/add', methods=['GET', 'POST'])
@admin_required
def product_new():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        category = (request.form.get("category") or "").strip()
        price_raw = (request.form.get("price_raw") or "").strip()
        image_url = (request.form.get("image_url") or "").strip()
        notes = (request.form.get("notes") or "").strip()
        stock = (request.form.get("stock") or "").strip()


        if not name or not category or not image_url:
            flash("Name or category is required", "error")
            return render_template("product_form.html", products=[], categories=categories)

        try:
            price = int(price_raw)
            if price <= 0:
                raise ValueError
        except ValueError:
            flash("Price must be a positive number", "error")
            return render_template("product_form.html", products=[], categories=categories)

        # Image url checker
        try:
            parsed = urlparse(image_url)
            if parsed.scheme not in ("http", "https"):
                raise ValueError
        except ValueError:
            flash("Invalid image URL", "error")
            return render_template("product_form.html", products=[], categories=categories)

        try:
            r = requests.get(image_url, timeout=5)
            content_type = r.headers.get("Content-Type", "")

            if content_type not in ("image/png", "image/jpeg"):
                flash("Image must be PNG, JPG, or JPEG", "error")
                return render_template("product_form.html", products=[], categories=categories)

        except requests.RequestException:
            flash("Could not reach image URL", "error")
            return render_template("product_form.html", products=[], categories=categories)

        prompt = (
            "First start with Општо:(bold in html format<b></b>, empty row, then the general things )"
            "Rewrite this short description in Macedonian."
            "Do not write too long in a row, if its too long split into another row"
            "Keep it friendly and short ( 2-3 sentences )."
            "Do not invent facts."
            "Give the product specifications in a 1 in a row format like this Спецификации:(bold in html format<b></b>, empty row, then the specifiactions in a new row)( Name in macedonian: Specification in english, example: Процесор: Intel Core i7 Quad-Core): Processor: --- DPI:--- Refresh Rate: --- depending on the product, also make it detailed and as much specifications that you can find"
            "Give me directly the description without any other additional things. Text: \n"
            f"{name}, {category}, {image_url}, {notes}"
        )

        ai_description = generate_text(prompt)

        product = Product(name=name, category=category, price=price, image_url=image_url, ai_description=ai_description, notes=notes or None, stock=stock)
        db_session.add(product)
        db_session.commit()

        log_action(f"[CREATE] Product ID={product.id}, Name='{product.name}'")

        return redirect(url_for("product_detail", product_id=product.id))
    return render_template('product_form.html', products=[], categories=categories)

@app.route('/products/<int:product_id>')
def product_detail(product_id):
    product = db_session.query(Product).get(product_id)
    if not product:
        return "No Product Found", 404

    products = db_session.query(Product).filter(Product.id != product_id).all()

    recommended = random.sample(
        products,
        min(len(products), 7)
    ) if products else []

    return render_template('product_detail.html', product=product, recommended=recommended, categories=categories)

@app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def product_edit(product_id: int):
    product = db_session.get(Product, product_id)
    if not product:
        return "No Product Found", 404

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        category = (request.form.get("category") or "").strip()
        price_raw = (request.form.get("price_raw") or "").strip()
        image_url = (request.form.get("image_url") or "").strip()
        # ai_description = (request.form.get("ai_description") or "").strip()
        notes = (request.form.get("notes") or "").strip()
        stock = (request.form.get("stock") or "").strip()

        if not name or not category or not image_url:
            flash("Name or category is required", "error")
            return render_template("product_form.html", product=product, categories=categories)

        try:
            price = int(price_raw)
            if price <= 0:
                raise ValueError
        except ValueError:
            flash("Price must be a positive number", "error")
            return render_template("product_form.html", product=product, categories=categories)

        prompt = (
            "First start with Општо:(bold in html format<b></b>, empty row, then the general things )"
            "Rewrite this short description in Macedonian."
            "Do not write too long in a row, if its too long split into another row"
            "Keep it friendly and short ( 2-3 sentences )."
            "Do not invent facts."
            "Give the product specifications in a 1 in a row format like this Спецификации:(bold in html format<b></b>, empty row, then the specifiactions in a new row)( Name in macedonian: Specification in english, example: Процесор: Intel Core i7 Quad-Core): Processor: --- DPI:--- Refresh Rate: --- depending on the product, also make it detailed and as much specifications that you can find"
            "Give me directly the description without any other additional things. Text: \n"
            f"{name}, {category}, {image_url}, {notes}"
        )

        # ai_description = generate_text(prompt)

        product.name = name
        product.category = category
        product.price = price
        product.image_url = image_url
        # product.ai_description = ai_description
        product.notes = notes or None
        product.stock = stock

        db_session.commit()

        log_action(f"[EDIT] Product ID={product.id}, Name='{product.name}'")

        return redirect(url_for("product_detail", product_id=product.id))
    return render_template('product_form.html', product=product, categories=categories)

@app.route('/products/<int:product_id>/delete', methods=['GET', 'POST'])
@admin_required
def product_delete(product_id: int):
    product = db_session.get(Product, product_id)
    if not product:
        return "No Product Found", 404

    log_action(f"[DELETE] Product ID={product.id}, Name='{product.name}'")

    db_session.delete(product)
    db_session.commit()
    return redirect(url_for("catalogue"))

@app.route("/cart/clear")
def cart_clear():
    cart_session["cart"] = {}
    return redirect(url_for("cart"))

@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def cart_add(product_id):
    product = db_session.get(Product, product_id)
    if not product:
        return "Product not found", 404

    cart = get_cart()
    pid = str(product_id)

    if pid in cart:
        cart[pid]["quantity"] += 1
    else:
        cart[pid] = {
            "name": product.name,
            "price": product.price,
            "image_url": product.image_url,
            "quantity": 1
        }

    flask_session.modified = True

    cart_session["cart"] = cart

    return redirect(url_for("cart"))

@app.route("/cart/remove/<int:product_id>")
@admin_required
def cart_remove(product_id):
    cart = get_cart()
    pid = str(product_id)

    if pid in cart:
        del cart[pid]
        cart_session.modified = True

    return redirect(url_for("cart"))

@app.route("/cart")
@login_required
def cart():
    cart = get_cart()
    total = sum(item["price"] * item["quantity"] for item in cart.values())
    return render_template("cart.html", cart=cart, total=total)

@app.route("/checkout")
@login_required
def checkout():
    cart = get_cart()

    if not cart:
        return redirect(url_for("cart"))

    total = sum(item["price"] * item["quantity"] for item in cart.values())

    return render_template("checkout.html", cart=cart, total=total)

@app.route("/checkout/confirm", methods=["POST"])
@login_required
def checkout_confirm():
    cart = get_cart()

    if not cart:
        return redirect(url_for("cart"))

    for pid, item in cart.items():
        product = db_session.get(Product, int(pid))
        if product:
            product.stock = max(0, product.stock - item["quantity"])
            db_session.add(product)

    db_session.commit()

    cart_session["cart"] = {}
    cart_session.modified = True

    return render_template("checkout_success.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier")
        password = request.form.get("password")

        user = db_session.query(User).filter(
            or_(
                User.username == identifier,
                User.email == identifier
            )
        ).first()

        if not user or not user.check_password(password):
            flash("Invalid credentials", "error")
            return redirect(url_for("login"))

        cart_session["user_id"] = user.id
        cart_session["username"] = user.username
        cart_session["is_admin"] = user.is_admin

        if user.is_admin:
            log_action(f"[LOGIN] Admin: '{user.username}' logged in")

        flash("Logged in successfully!", "success")
        return redirect(url_for("home"))

    return render_template("auth.html", mode="login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = db_session.query(User).filter(
            or_(
                User.username == username,
                User.email == email
            )
        ).first()

        if existing_user:
            flash("Username or email already exists", "error")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            email=email,
            verified=True,
            verification_code="none"
        )

        new_user.set_password(password)

        db_session.add(new_user)
        db_session.commit()

        log_action(f"[REGISTER] User '{username}' created")

        flash("Account created!", "success")
        return redirect(url_for("login"))

    return render_template("auth.html", mode="register")

@app.route("/logout")
def logout():
    username = cart_session.get("username")
    is_admin = cart_session.get("is_admin")

    if is_admin:
        log_action(f"[LOGOUT] Admin: '{username}' logged out")

    cart_session.clear()

    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

@app.route("/dashboard")
@admin_required
def dashboard():
    from models import User, Product, Log

    total_users = db_session.query(User).count()
    total_products = db_session.query(Product).count()
    total_logs = db_session.query(Log).count()

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_products=total_products,
        total_logs=total_logs
    )

@app.route("/dashboard/logs")
@admin_required
def logs():
    logs = db_session.query(Log).order_by(Log.timestamp.desc()).all()
    return render_template("logs.html", logs=logs)

@app.route("/dashboard/users")
@admin_required
def view_users():
    users = db_session.query(User).all()
    return render_template("users.html", users=users)


@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(debug=True)