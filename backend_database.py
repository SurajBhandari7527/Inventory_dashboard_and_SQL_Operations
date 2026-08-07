import mysql.connector
import streamlit as st

def connect_to_db():
    """Connects to Aiven MySQL database using Streamlit secrets and required SSL."""
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=int(st.secrets["mysql"]["port"]),
    )

def basic_data(cursor):
    queries = {
        "Total suppliers": "SELECT COUNT(supplier_id) AS total_suppliers FROM suppliers",
        "Total Products": "SELECT COUNT(*) AS total_products FROM products",
        "Total categories dealing": "SELECT COUNT(DISTINCT category) AS total_categories FROM products",
        "Total sales value made in last 3 months": """
            SELECT SUM(ABS(t.change_quantity) * t.price) 
            FROM (
                SELECT se.product_id, se.change_quantity, p.price, se.entry_date 
                FROM stock_entries AS se 
                LEFT JOIN products AS p ON se.product_id = p.product_id 
                WHERE se.change_quantity < 0 
                AND se.entry_date >= (
                    SELECT DATE_SUB(MAX(s.entry_date), INTERVAL 3 MONTH) FROM stock_entries AS s
                )
            ) AS t
        """,
        "Total Restock Value (Last 3 Months)": """
            SELECT ROUND(SUM(se.change_quantity * p.price), 2) AS total_restock
            FROM stock_entries se
            JOIN products p ON se.product_id = p.product_id
            WHERE se.change_type = 'Restock'
            AND se.entry_date >= (
                SELECT DATE_SUB(MAX(entry_date), INTERVAL 3 MONTH) FROM stock_entries
            )
        """,
        "below reorder threshold and no pending orders": """
            SELECT COUNT(DISTINCT product_id) 
            FROM products AS p
            WHERE p.product_id NOT IN (
                SELECT DISTINCT product_id FROM reorders WHERE status = 'Pending'
            ) 
            AND p.stock_quantity < p.reorder_level
        """
    }

    result = {}
    for label, query in queries.items():
        cursor.execute(query)
        value = cursor.fetchone()
        # Extract the first value safely
        result[label] = list(value.values())[0] if value else 0
    return result

def get_table_details(cursor):
    queries = {
        "Supplier details": "SELECT supplier_name, contact_name, email, phone FROM suppliers",
        "Product stock details details": """
            SELECT p.product_name, p.stock_quantity, p.reorder_level, s.supplier_name 
            FROM products AS p
            LEFT JOIN suppliers AS s ON p.supplier_id = s.supplier_id
        """,
        "Product needing reorder": """
            SELECT p.product_name, p.stock_quantity, p.reorder_level 
            FROM products AS p
            LEFT JOIN reorders AS r ON p.product_id = r.product_id
            WHERE p.stock_quantity < p.reorder_level 
            AND p.product_id NOT IN (
                SELECT DISTINCT product_id FROM reorders WHERE status = 'Pending' OR status = 'Ordered'
            )
        """
    }
    result = {}
    for label, query in queries.items():
        cursor.execute(query)
        table = cursor.fetchall()
        result[label] = table
    return result

def add_new_product_id(cursor, conn, p_name, p_category, p_price, p_quantity, p_reorder, p_supplier):
    procedure_call = "CALL AddNewProductManualID(%s, %s, %s, %s, %s, %s)"
    params = (p_name, p_category, p_price, p_quantity, p_reorder, p_supplier)
    cursor.execute(procedure_call, params)
    conn.commit()

def find_unique_categories(cursor):
    query = "SELECT DISTINCT category FROM products"
    cursor.execute(query)
    rows = cursor.fetchall()
    values = [d.get('category') for d in rows if d.get('category')]
    return values

def find_unique_suppliers(cursor):
    query = "SELECT DISTINCT supplier_id, supplier_name FROM suppliers"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def products_stock_history(cursor, product_id):
    query = """
        SELECT se.product_id, entry_date AS record_date, change_quantity AS Quantity, change_type
        FROM stock_entries AS se
        WHERE se.product_id = %s
        ORDER BY record_date DESC
    """
    params = (product_id,)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return rows

def product_status(cursor, product_id):
    query = """
        SELECT p.product_id, p.stock_quantity, p.reorder_level, p.supplier_id, s.supplier_name 
        FROM products AS p
        JOIN suppliers AS s ON p.supplier_id = s.supplier_id 
        WHERE p.product_id = %s
    """
    params = (product_id,)
    cursor.execute(query, params)
    row = cursor.fetchall()
    return row

def products_shipment_history(cursor, product_id, filter):
    if filter:
        query = """
            SELECT DISTINCT * FROM (
                SELECT r.product_id AS product_id, r.reorder_quantity AS quantity, r.reorder_date AS order_date, r.status 
                FROM reorders AS r
                UNION ALL
                SELECT s.product_id AS product_id, s.quantity_received AS quantity, s.shipment_date AS order_date, 'Received' AS status 
                FROM shipments AS s
            ) AS t 
            WHERE t.product_id = %s AND t.status = 'Ordered' 
            ORDER BY t.order_date DESC
        """
        params = (product_id,)
        cursor.execute(query, params)
        rows = cursor.fetchall()
    else:
        query = """
            SELECT DISTINCT * FROM (
                SELECT r.product_id AS product_id, r.reorder_quantity AS quantity, r.reorder_date AS order_date, r.status 
                FROM reorders AS r
                UNION ALL
                SELECT s.product_id AS product_id, s.quantity_received AS quantity, s.shipment_date AS order_date, 'Received' AS status 
                FROM shipments AS s
            ) AS t 
            WHERE t.product_id = %s 
            ORDER BY t.order_date DESC
        """
        params = (product_id,)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
    return rows

def find_all_products(cursor):
    query = "SELECT DISTINCT product_id, product_name FROM products"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def place_reorder(cursor, conn, product_id, quantity):
    query = """
        INSERT INTO reorders(reorder_id, product_id, reorder_quantity, reorder_date, status)
        SELECT COALESCE(MAX(reorder_id), 0) + 1, %s, %s, CURDATE(), 'Ordered' 
        FROM reorders
    """
    params = (product_id, quantity)
    cursor.execute(query, params)
    conn.commit()

def receive_reorder(cursor, conn, reorder_id):
    query = "CALL receive_reorder(%s)"
    params = (reorder_id,)
    cursor.execute(query, params)
    conn.commit()

def find_reorder_id_details(cursor):
    query = "SELECT r.reorder_id, r.product_id, p.product_name FROM reorders r LEFT JOIN products p ON r.product_id = p.product_id"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows
