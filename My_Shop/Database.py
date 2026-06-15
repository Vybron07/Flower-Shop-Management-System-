import sqlite3

DB_NAME = "shop.db"

def connect():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = connect()
    cur = conn.cursor()

    # Flowers/inventory table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shop (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            flower_type TEXT DEFAULT '',
            total_stock INTEGER DEFAULT 1,
            available_stock INTEGER DEFAULT 1,
            condition TEXT DEFAULT 'Fresh',
            cover_image BLOB,
            added_date TEXT DEFAULT (DATE('now'))
        )
    """)

    # Customers table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            joined_date TEXT DEFAULT (DATE('now')),
            active INTEGER DEFAULT 1
        )
    """)

    # Staff table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'Manager',
            email TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            joined_date TEXT DEFAULT (DATE('now')),
            active INTEGER DEFAULT 1
        )
    """)

    # Orders table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            order_date TEXT DEFAULT (DATETIME('now')),
            total_amount REAL DEFAULT 0.0,
            discount REAL DEFAULT 0.0,
            final_amount REAL DEFAULT 0.0,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (staff_id) REFERENCES staff(id)
        )
    """)

    # Order items table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            flower_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (flower_id) REFERENCES shop(id)
        )
    """)

    # Default admin account
    cur.execute("""
        INSERT OR IGNORE INTO staff (name, username, password, role)
        VALUES ('Admin', 'admin', 'admin123', 'Admin')
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


# ── Flower functions ────────────────────────────────────────

def add_flower(name, price, flower_type="", condition="Fresh", stock=1, cover=None):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO shop (name, price, flower_type, total_stock, available_stock, condition, cover_image)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, price, flower_type, stock, stock, condition, cover))
    conn.commit()
    conn.close()

def get_all_flowers():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM shop")
    flowers = cur.fetchall()
    conn.close()
    return flowers

def search_flowers(keyword):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM shop
        WHERE name LIKE ? OR flower_type LIKE ? OR condition LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    flowers = cur.fetchall()
    conn.close()
    return flowers

def filter_flowers(condition=None, available_only=False):
    conn = connect()
    cur = conn.cursor()
    query = "SELECT * FROM shop WHERE 1=1"
    params = []
    if condition:
        query += " AND condition = ?"
        params.append(condition)
    if available_only:
        query += " AND available_stock > 0"
    cur.execute(query, params)
    flowers = cur.fetchall()
    conn.close()
    return flowers

def update_flower_condition(flower_id, condition):
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE shop SET condition = ? WHERE id = ?", (condition, flower_id))
    conn.commit()
    conn.close()

def delete_flower(flower_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM shop WHERE id = ?", (flower_id,))
    conn.commit()
    conn.close()

def get_low_stock_flowers(threshold=5):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM shop WHERE available_stock <= ?", (threshold,))
    flowers = cur.fetchall()
    conn.close()
    return flowers


# ── Customer functions ──────────────────────────────────────

def add_customer(name, email="", phone=""):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO customers (name, email, phone)
        VALUES (?, ?, ?)
    """, (name, email, phone))
    conn.commit()
    conn.close()

def get_all_customers():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE active = 1")
    customers = cur.fetchall()
    conn.close()
    return customers

def delete_customer(customer_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE customers SET active = 0 WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()


# ── Staff functions ─────────────────────────────────────────

def verify_login(username, password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM staff WHERE username = ? AND password = ? AND active = 1
    """, (username, password))
    staff = cur.fetchone()
    conn.close()
    return staff

def add_staff(name, username, password, role="Manager", email="", phone=""):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO staff (name, username, password, role, email, phone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, username, password, role, email, phone))
    conn.commit()
    conn.close()

def get_all_staff():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM staff WHERE active = 1")
    staff = cur.fetchall()
    conn.close()
    return staff


# ── Order functions ─────────────────────────────────────────

def create_order(customer_id, staff_id, items, discount=0.0):
    conn = connect()
    cur = conn.cursor()
    total = sum(i["quantity"] * i["unit_price"] for i in items)
    final = total - (total * discount / 100)
    cur.execute("""
        INSERT INTO orders (customer_id, staff_id, total_amount, discount, final_amount)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, staff_id, total, discount, final))
    order_id = cur.lastrowid
    for item in items:
        subtotal = item["quantity"] * item["unit_price"]
        cur.execute("""
            INSERT INTO order_items (order_id, flower_id, quantity, unit_price, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, item["flower_id"], item["quantity"], item["unit_price"], subtotal))
        cur.execute("""
            UPDATE shop SET available_stock = available_stock - ? WHERE id = ?
        """, (item["quantity"], item["flower_id"]))
    conn.commit()
    conn.close()
    return order_id

def get_all_orders():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.id, c.name as customer, s.name as staff,
               o.order_date, o.total_amount, o.discount,
               o.final_amount, o.status
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        JOIN staff s ON o.staff_id = s.id
        ORDER BY o.order_date DESC
    """)
    orders = cur.fetchall()
    conn.close()
    return orders

def get_order_details(order_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.id, c.name as customer, c.phone as customer_phone,
               s.name as staff, o.order_date,
               o.total_amount, o.discount, o.final_amount, o.status
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        JOIN staff s ON o.staff_id = s.id
        WHERE o.id = ?
    """, (order_id,))
    order = cur.fetchone()
    cur.execute("""
        SELECT f.name as flower, oi.quantity, oi.unit_price, oi.subtotal
        FROM order_items oi
        JOIN shop f ON oi.flower_id = f.id
        WHERE oi.order_id = ?
    """, (order_id,))
    items = cur.fetchall()
    conn.close()
    return order, items

def update_order_status(order_id, status):
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()

def get_order_stats():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders")
    total_orders = cur.fetchone()[0]
    cur.execute("SELECT SUM(final_amount) FROM orders")
    total_revenue = cur.fetchone()[0] or 0.0
    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'Pending'")
    pending = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM orders WHERE DATE(order_date) = DATE('now')")
    today_orders = cur.fetchone()[0]
    conn.close()
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending": pending,
        "today_orders": today_orders
    }


# ── Dashboard stats ─────────────────────────────────────────

def get_stats():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM shop")
    total_flowers = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM customers WHERE active = 1")
    total_customers = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'Completed'")
    total_sold = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'Pending'")
    pending = cur.fetchone()[0]
    conn.close()
    return {
        "total_flowers": total_flowers,
        "total_customers": total_customers,
        "total_sold": total_sold,
        "pending": pending
    }


if __name__ == "__main__":
    initialize_db()
