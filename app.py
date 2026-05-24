print("RUNNING CLEAN VERSION")

from flask import Flask, render_template, request, redirect, session, flash
from database.db_config import get_db_connection

app = Flask(__name__)
app.secret_key = "secret123"



# HOME → redirect dashboard
# -------------------------
@app.route("/")
def home():
    return redirect("/dashboard")


# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                       (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session["user"] = user["username"]
            return redirect("/dashboard")
        else:
            return "Wrong username or password"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) FROM customers")
    customers = cursor.fetchone()["COUNT(*)"]

    cursor.execute("SELECT COUNT(*) FROM products")
    products = cursor.fetchone()["COUNT(*)"]

    cursor.execute("SELECT COUNT(*) FROM orders")
    orders = cursor.fetchone()["COUNT(*)"]

    cursor.execute("""
        SELECT COUNT(*) FROM orders
        JOIN order_items ON orders.id = order_items.order_id
        JOIN products ON order_items.product_id = products.id
        WHERE products.category = 'grooming'
    """)
    grooming_count = cursor.fetchone()["COUNT(*)"]

    cursor.execute("""
        SELECT COUNT(*) FROM orders
        JOIN order_items ON orders.id = order_items.order_id
        JOIN products ON order_items.product_id = products.id
        WHERE products.category != 'grooming'
    """)
    product_sales = cursor.fetchone()["COUNT(*)"]

    cursor.execute("""
        SELECT COUNT(*) FROM products
        WHERE stock < 5
    """)
    low_stock = cursor.fetchone()["COUNT(*)"]



    cursor.execute("""
        SELECT category, COUNT(*) AS total
        FROM products
        GROUP BY category
    """)

    category_stats = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        customers=customers,
        products=products,
        orders=orders,
        grooming_count=grooming_count,
        product_sales=product_sales,
        low_stock=low_stock,
        category_stats=category_stats
    )


# -------------------------
# CUSTOMERS
# -------------------------
@app.route("/customers", methods=["GET", "POST"])
def customers():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        cursor.execute(
            "INSERT INTO customers (name, email, phone, address) VALUES (%s, %s, %s, %s)",
            (name, email, phone, address)
        )
        conn.commit()

        flash("Customer added successfully")

    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    conn.close()

    return render_template("customers.html", customers=customers)


@app.route("/delete_customer/<int:id>")
def delete_customer(id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM orders WHERE customer_id=%s", (id,))
    customer_orders = cursor.fetchall()

    for order in customer_orders:
        cursor.execute(
            "DELETE FROM order_items WHERE order_id=%s",
            (order["id"],)
        )

    cursor.execute(
        "DELETE FROM orders WHERE customer_id=%s",
        (id,)
    )

    cursor.execute(
        "DELETE FROM customers WHERE id=%s",
        (id,)
    )

    conn.commit()
    conn.close()

    flash("Customer deleted successfully")

    return redirect("/customers")

@app.route("/edit_customer/<int:id>")
def edit_customer(id):

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM customers WHERE id = %s", (id,))
    customer = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit_customer.html", customer=customer)

@app.route("/update_customer/<int:id>", methods=["GET", "POST"])
def update_customer(id):

    if "user" not in session:
        return redirect("/login")

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    address = request.form["address"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    UPDATE customers SET name = %s, email = %s, phone = %s, address = %s WHERE id = %s
    """, (name, email, phone, address, id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/customers")





# -------------------------
# PRODUCTS
# -------------------------
@app.route("/products", methods=["GET", "POST"])
def products():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form.get("name")
        category = request.form.get("category")
        supplier = request.form.get("supplier")
        price = request.form.get("price")
        stock = request.form.get("stock")

        sql = """
        INSERT INTO products (name, category, supplier, price, stock)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (name, category, supplier, price, stock)

        cursor.execute(sql, values)
        conn.commit()

        flash("Product added successfully")

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template("products.html", products=products)


@app.route("/delete_product/<int:id>")
def delete_product(id):

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("DELETE FROM order_items WHERE product_id = %s", (id,))
    conn.commit()

    cursor.execute("DELETE FROM products WHERE id = %s", (id,))
    conn.commit()

    conn.close()

    return redirect("/products")


@app.route("/edit_product/<int:id>" ,methods=["GET", "POST"])
def edit_product(id):

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        supplier = request.form["supplier"]
        price = request.form["price"]
        stock = request.form["stock"]

        cursor.execute("""
            UPDATE products
            SET name=%s, category=%s, supplier=%s, price=%s, stock=%s
            WHERE id=%s
        """, (name, category, supplier, price, stock, id))

        conn.commit()
        conn.close()

        return redirect("/products")

    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cursor.fetchone()

    conn.close()

    return render_template("edit_product.html", product=product)



# -------------------------
# ORDERS
# -------------------------
@app.route("/orders", methods=["GET", "POST"])
def orders():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    filter_type = request.args.get("type")

    # Load customers
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    # Load products
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    # CREATE ORDER
    if request.method == "POST":

        customer_id = request.form.get("customer_id")
        product_id = request.form.get("product_id")
        quantity = request.form.get("quantity")

        pet_name = request.form.get("pet_name")
        appointment_date = request.form.get("appointment_date")
        appointment_time = request.form.get("appointment_time")

        if not customer_id or not product_id or not quantity:
            conn.close()
            return "Missing form data"

        quantity = int(quantity)

        cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = cursor.fetchone()

        if not product:
            conn.close()
            return "Product not found"

        # Stock check
        if product["category"] != "grooming":
            if quantity > product["stock"]:
                conn.close()
                return "Not enough stock"

        # Grooming slot check
        if product["category"] == "grooming":

            cursor.execute("""
                SELECT *
                FROM orders
                WHERE appointment_date=%s
                AND appointment_time=%s
            """, (appointment_date, appointment_time))

            existing_appointment = cursor.fetchone()

            if existing_appointment:
                conn.close()
                return "This appointment slot is already booked"

        # Insert order
        cursor.execute("""
            INSERT INTO orders (customer_id, appointment_date, appointment_time, pet_name)
            VALUES (%s, %s, %s, %s)
        """, (customer_id, appointment_date, appointment_time, pet_name))

        order_id = cursor.lastrowid

        # Insert order item
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity)
            VALUES (%s, %s, %s)
        """, (order_id, product_id, quantity))

        # Update stock
        if product["category"] != "grooming":

            new_stock = product["stock"] - quantity

            cursor.execute("""
                UPDATE products
                SET stock=%s
                WHERE id=%s
            """, (new_stock, product_id))

        conn.commit()

    # FILTER
    if filter_type == "grooming":

        cursor.execute("""
            SELECT
                orders.id,
                customers.name AS customer_name,
                products.name AS product_name,
                products.category,
                order_items.quantity,
                orders.pet_name,
                orders.appointment_date,
                orders.appointment_time
            FROM orders
            JOIN customers ON orders.customer_id = customers.id
            JOIN order_items ON orders.id = order_items.order_id
            JOIN products ON order_items.product_id = products.id
            WHERE products.category = 'grooming'
        """)

    elif filter_type == "product":

        cursor.execute("""
            SELECT
                orders.id,
                customers.name AS customer_name,
                products.name AS product_name,
                products.category,
                order_items.quantity,
                orders.pet_name,
                orders.appointment_date,
                orders.appointment_time
            FROM orders
            JOIN customers ON orders.customer_id = customers.id
            JOIN order_items ON orders.id = order_items.order_id
            JOIN products ON order_items.product_id = products.id
            WHERE products.category != 'grooming'
        """)

    else:

        cursor.execute("""
            SELECT
                orders.id,
                customers.name AS customer_name,
                products.name AS product_name,
                products.category,
                order_items.quantity,
                orders.pet_name,
                orders.appointment_date,
                orders.appointment_time
            FROM orders
            JOIN customers ON orders.customer_id = customers.id
            JOIN order_items ON orders.id = order_items.order_id
            JOIN products ON order_items.product_id = products.id
        """)

    orders = cursor.fetchall()

    cursor.execute("""
        SELECT
            customers.name AS customer_name,
            orders.pet_name,
            orders.appointment_date,
            orders.appointment_time
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        JOIN order_items ON orders.id = order_items.order_id
        JOIN products ON order_items.product_id = products.id
        WHERE products.category = 'grooming'
        ORDER BY orders.appointment_date, orders.appointment_time
    """)

    appointments = cursor.fetchall()

    cursor.execute("""
        SELECT
            customers.name AS customer_name,
            products.name AS product_name,
            orders.pet_name,
            orders.appointment_date,
            orders.appointment_time
        FROM orders
        JOIN customers ON orders.customer_id = customers.id
        JOIN order_items ON orders.id = order_items.order_id
        JOIN products ON order_items.product_id = products.id
        WHERE products.category = 'grooming'
        ORDER BY orders.appointment_date ASC,
                 orders.appointment_time ASC
    """)

    grooming_orders = cursor.fetchall()

    conn.close()

    return render_template(
        "orders.html",
        customers=customers,
        products=products,
        orders=orders,
        grooming_orders=grooming_orders
    )


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)