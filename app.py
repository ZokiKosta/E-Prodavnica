import random
from urllib.parse import urlparse

import flask_session
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import or_

from database import session
from models import Product
from flask import session as cart_session

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
    products = session.query(Product).all()

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

    query = session.query(Product)

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
    session.close()

    return render_template('catalogue.html', categories=categories, q=q,category=category, products=products, page=page, total_pages=total_pages)

@app.route('/products/add', methods=['GET', 'POST'])
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
        session.add(product)
        session.commit()
        return redirect(url_for("product_detail", product_id=product.id))
    return render_template('product_form.html', products=[], categories=categories)

@app.route('/products/<int:product_id>')
def product_detail(product_id):
    product = session.query(Product).get(product_id)
    if not product:
        return "No Product Found", 404

    products = session.query(Product).filter(Product.id != product_id).all()

    recommended = random.sample(
        products,
        min(len(products), 7)
    ) if products else []

    return render_template('product_detail.html', product=product, recommended=recommended, categories=categories)

@app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
def product_edit(product_id: int):
    product = session.get(Product, product_id)
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

        session.commit()
        return redirect(url_for("product_detail", product_id=product.id))
    return render_template('product_form.html', product=product, categories=categories)

@app.route('/products/<int:product_id>/delete', methods=['GET', 'POST'])
def product_delete(product_id: int):
    product = session.get(Product, product_id)
    if not product:
        return "No Product Found", 404

    session.delete(product)
    session.commit()
    return redirect(url_for("catalogue"))

@app.route("/cart/clear")
def cart_clear():
    cart_session["cart"] = {}
    return redirect(url_for("cart"))

@app.route("/cart/add/<int:product_id>", methods=["POST"])
def cart_add(product_id):
    product = session.get(Product, product_id)
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
def cart_remove(product_id):
    cart = get_cart()
    pid = str(product_id)

    if pid in cart:
        del cart[pid]
        cart_session.modified = True

    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    cart = get_cart()
    total = sum(item["price"] * item["quantity"] for item in cart.values())
    return render_template("cart.html", cart=cart, total=total)

@app.route("/checkout")
def checkout():
    cart = get_cart()

    if not cart:
        return redirect(url_for("cart"))

    total = sum(item["price"] * item["quantity"] for item in cart.values())

    return render_template("checkout.html", cart=cart, total=total)

@app.route("/checkout/confirm", methods=["POST"])
def checkout_confirm():
    cart = get_cart()

    if not cart:
        return redirect(url_for("cart"))

    for pid, item in cart.items():
        product = session.get(Product, int(pid))
        if product:
            product.stock = max(0, product.stock - item["quantity"])
            session.add(product)

    session.commit()

    cart_session["cart"] = {}
    cart_session.modified = True

    return render_template("checkout_success.html")


@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(debug=True)