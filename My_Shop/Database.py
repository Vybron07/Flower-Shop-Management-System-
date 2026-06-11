import sqlite3
import os 

DB_NAME = 'shop.db'

def connect():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect()
    cur = conn.cursor()

    #Flower Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shop(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Flower_Name TEXT NOT NULL,
            Customer TEXT NOT NULL,
            Price REAL NOT NULL,
            isbn TEXT UNIQUE,
            total_Stock INTEGER DEFAULT 1,
            Available_Stock INTEGER DEFAULT 1,
            Condition TEXT DEFAULT 'Fresh',
            cover_image BLOB,
            added_date TEXT DEFAULT (DATE('now'))
        )
    """)

     # Customers table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            Bought_date TEXT DEFAULT (DATE('now')),
        )
    """)
    # Staff table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            Role TEXT DEFAULT 'Librarian',
            email TEXT,
            Phone TEXT,
            Joined_date TEXT DEFAULT (DATE('now')),
            active INTEGER DEFAULT 1
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


# System Functions

def add_flower(Flower_Name, Customer, Price, isbn="", total_Stock=1, Available_Stock=1, Condition="Fresh", cover_image=None):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO shop (Flower_Name, Customer, Price, isbn, total_Stock, Available_Stock, Condition, cover_image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (Flower_Name, Customer, Price, isbn, total_Stock, Available_Stock, Condition, cover_image))
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
        WHERE Flower_Name LIKE ? OR Customer LIKE ? OR Condition LIKE ? OR isbn LIKE ?
    """, (f"%{keyword}%",) * 4)
    flowers = cur.fetchall()
    conn.close()
    return flowers

def filter_flowers(condition=None, available_only=False):
    conn = connect()
    cur = conn.cursor()
    query = "SELECT * FROM shop WHERE 1=1"
    params = []
    if condition:
        query += " AND Condition = ?"
        params.append(condition)
    if available_only:
        query += " AND Available_Stock > 0"
    cur.execute(query, params)
    flowers = cur.fetchall()
    conn.close()
    return flowers

def update_flower_condition(flower_id, condition):
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE shop SET Condition = ? WHERE id = ?", (condition, flower_id))
    conn.commit()
    conn.close()

def delete_flower(flower_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM shop WHERE id = ?", (flower_id,))
    conn.commit()
    conn.close()

#Customer_Functions

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
    cur.execute("SELECT * FROM customers")
    customers = cur.fetchall()
    conn.close()
    return customers

def delete_customer(customer_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()

#Staff_Functions

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

# Issue

def sold_flower(flower_id, customer_id, bought_by, returned_date):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO issued_flowers (flower_id, customer_id, issued_by, due_date)
        VALUES (?, ?, ?, ?)
    """, (flower_id, customer_id, issued_by, due_date))
    cur.execute("""
        UPDATE shop SET Available_Stock = Available_Stock - 1 WHERE id = ?
    """, (flower_id,))
    conn.commit()
    conn.close()


def return_flower(issue_id, fine=0.0):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        UPDATE sold_flowers
        SET return_date = DATE('now'), fine = ?, status = 'Returned'
        WHERE id = ?
    """, (fine, issue_id))
    cur.execute("""
        UPDATE shop SET Available_Stock = Available_Stock + 1
        WHERE id = (SELECT flower_id FROM sold_flowers WHERE id = ?)
    """, (issue_id,))
    conn.commit()
    conn.close()

def get_sold_flowers():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT sf.id, f.Flower_Name, c.name as customer, sf.issued_date, sf.due_date, sf.status
        FROM sold_flowers sf
        JOIN shop f ON sf.flower_id = f.id
        JOIN customers c ON sf.customer_id = c.id
        WHERE sf.status = 'Sold'
    """)
    records = cur.fetchall()
    conn.close()
    return records

#Dashboard Stats

def get_stats():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM shop")
    total_flowers = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM customers WHERE active = 1")
    total_customers = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM sold_flowers WHERE status = 'Sold'")
    total_sold = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM issued_flowers WHERE due_date < DATE('now') AND status = 'Issued'")
    overdue = cur.fetchone()[0]
    conn.close()
    return {
        "total_flowers": total_flowers,
        "total_customers": total_customers,
        "total_sold": total_sold,
        "overdue": overdue
    }

if __name__ == "__main__":
    initialize_db()


