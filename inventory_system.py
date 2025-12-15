import mysql.connector
from mysql.connector import Error

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # No password, since you run MariaDB without one
        database="inventory_db"
    )

def setup_database():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_db")
        cursor.execute("USE inventory_db")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                price DECIMAL(10,2),
                quantity INT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT,
                quantity_sold INT,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        db.commit()
        db.close()
    except Error as e:
        print("❌ Database setup error:", e)

def add_product():
    try:
        name = input("Enter product name: ")
        price = float(input("Enter price: "))
        quantity = int(input("Enter quantity: "))
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)",
            (name, price, quantity)
        )
        db.commit()
        db.close()
        print("✅ Product added successfully")
    except ValueError:
        print("❌ Invalid input")
    except Error as e:
        print("❌ Error:", e)

def view_products():
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        print("\n--- AVAILABLE PRODUCTS ---")
        if not products:
            print("No products found.")
        else:
            for p in products:
                print(f"ID: {p[0]} | Name: {p[1]} | Price: {p[2]} | Stock: {p[3]}")
        db.close()
    except Error as e:
        print("❌ Error:", e)

def record_sale():
    try:
        product_id = int(input("Enter product ID: "))
        quantity_sold = int(input("Quantity sold: "))
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT quantity FROM products WHERE id = %s", (product_id,))
        stock = cursor.fetchone()
        if not stock:
            print("❌ Product not found")
            db.close()
            return
        if stock[0] < quantity_sold:
            print("❌ Not enough stock")
            db.close()
            return
        cursor.execute(
            "INSERT INTO sales (product_id, quantity_sold) VALUES (%s, %s)",
            (product_id, quantity_sold)
        )
        cursor.execute(
            "UPDATE products SET quantity = quantity - %s WHERE id = %s",
            (quantity_sold, product_id)
        )
        db.commit()
        db.close()
        print("✅ Sale recorded successfully")
    except ValueError:
        print("❌ Invalid input")
    except Error as e:
        print("❌ Error:", e)

def sales_report():
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT p.name, SUM(s.quantity_sold) AS total_sold
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.name
        """)
        report = cursor.fetchall()
        print("\n--- SALES REPORT ---")
        if not report:
            print("No sales recorded.")
        else:
            for r in report:
                print(f"Product: {r[0]} | Total Sold: {r[1]}")
        db.close()
    except Error as e:
        print("❌ Error:", e)

def main():
    setup_database()
    while True:
        print("""
==============================
SALES & INVENTORY SYSTEM
==============================
1. Add Product
2. View Products
3. Record Sale
4. Sales Report
5. Exit
""")
        choice = input("Choose an option: ")
        if choice == "1":
            add_product()
        elif choice == "2":
            view_products()
        elif choice == "3":
            record_sale()
        elif choice == "4":
            sales_report()
        elif choice == "5":
            print("👋 Exiting system")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
