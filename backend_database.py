import mysql.connector
import streamlit as st

def connect_to_db():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=int(st.secrets["mysql"]["port"]),
    )
     

def basic_data(cursor):
    queries={
        "Total suppliers": "Select count(supplier_id) as total_suppliers from suppliers",
        "Total Products":"SELECT COUNT(*) as total_products from products",
        "Total categories dealing":"Select count(distinct(category)) as total_categories from products",
        "Total sales value made in last 3 months": """select sum(abs(t.change_quantity) * t.price) from 
(select se.product_id,se.change_quantity,p.price,se.entry_date from stock_entries as se 
left join products as p 
on se.product_id = p.product_id 
where se.change_quantity<0 and 
se.entry_date >= (
select date_sub(max(s.entry_date), interval 3 month) from stock_entries as s
))
as t""",
"Total Restock Value (Last 3 Months)": """
SELECT ROUND(SUM(se.change_quantity * p.price), 2) AS total_restock
FROM stock_entries se
JOIN products p ON se.product_id = p.product_id
WHERE se.change_type = 'Restock'
AND se.entry_date >= (
SELECT DATE_SUB(MAX(entry_date), INTERVAL 3 MONTH) FROM stock_entries
)
""",
    "below reorder threshold and no pending orders":
    """select count(distinct(product_id)) from products as p
where  p.product_id NOT IN ( select distinct(product_id) from reorders where status='Pending') and
 p.stock_quantity<p.reorder_level"""
    }

    result={}
    for label in queries:
        cursor.execute(queries[label])
        value=cursor.fetchone()
        result[label]=list(value.values())[0]
    return result

def get_table_details(cursor):
    queries={"Supplier details":"SELECT supplier_name,contact_name,email,phone FROM suppliers",
             "Product stock details details": """select p.product_name,p.stock_quantity,p.reorder_level,s.supplier_name from products as p
left join suppliers as s
on p.supplier_id=s.supplier_id""",
"Product needing reorder":"""select p.product_name,p.stock_quantity,p.reorder_level from products as p
    left join reorders as r
    on p.product_id=r.product_id
where p.stock_quantity < p.reorder_level and p.product_id NOT IN (select distinct(product_id) from reorders where status='Pending' or status='Ordered' )"""

   }
    result={}
    for label,query in queries.items():
        cursor.execute(query)
        table=cursor.fetchall()
        result[label]=table
    return result


def add_new_product_id(cursor,conn,p_name,p_category, p_price,p_quantity,p_reorder,p_supplier):
    procedure_call="Call AddNewProductManualID(%s, %s, %s ,%s, %s, %s)"
    params=(p_name,p_category, p_price,p_quantity,p_reorder,p_supplier)
    cursor.execute(procedure_call,params)
    conn.commit()
    
def find_unique_categories(cursor):
    query="Select distinct(category) from products"
    cursor.execute(query)
    rows=list(cursor.fetchall())
    values=[d.get('category') for d in rows ]
    return values

def find_unique_suppliers(cursor):
    query="Select distinct(supplier_id),supplier_name from suppliers"
    cursor.execute(query)
    rows=cursor.fetchall()
    return rows

def products_stock_history(cursor,product_id):
    query="""select
se.product_id ,
entry_date as record_date,
change_quantity as Quantity,
change_type
from stock_entries as se
where se.product_id=%s
order by record_date desc"""
    params=(product_id,)
    cursor.execute(query,params)
    rows=cursor.fetchall()
    return rows

def product_status(cursor,product_id):
    query="""SELECT p.product_id,p.stock_quantity,p.reorder_level,p.supplier_id,s.supplier_name FROM products as p
 join suppliers as s on p.supplier_id=s.supplier_id where p.product_id=%s"""
    params=(product_id,)
    cursor.execute(query,params)
    row=cursor.fetchall()
    
    return row

def products_shipment_history(cursor,product_id,filter):
    
    if filter:
        query="""  select distinct * from(SELECT  r.product_id as product_id, r.reorder_quantity as quantity, r.reorder_date as order_date, r.status FROM reorders as r
        union all
        select s.product_id as product_id,s.quantity_received as quantity, s.shipment_date as order_date, "Received" as status from shipments as s)
        as t 
        where t.product_id=%s and t.status="Ordered" order by t.order_date desc"""
        params=(product_id,)
        cursor.execute(query,params)
        rows=cursor.fetchall()
    else:
        query="""  select distinct * from(SELECT  r.product_id as product_id, r.reorder_quantity as quantity, r.reorder_date as order_date, r.status FROM reorders as r
        union all
        select s.product_id as product_id,s.quantity_received as quantity, s.shipment_date as order_date, "Received" as status from shipments as s)
        as t 
        where t.product_id=%s order by t.order_date desc"""
        params=(product_id,)
        cursor.execute(query,params)
        rows=cursor.fetchall()
        
    return rows

def find_all_products(cursor):
    query="select distinct(product_id),product_name from products"
    cursor.execute(query)
    rows=cursor.fetchall()
    print(rows)
    return rows

def place_reorder(cursor,conn,product_id,quantity):
    query="""insert into reorders(reorder_id,product_id,reorder_quantity,reorder_date,status)
select max(reorder_id)+1,%s,%s,curdate(),"Ordered" from reorders"""
    params=(product_id,quantity)
    cursor.execute(query,params)
    conn.commit()

def receive_reorder(cursor,conn,reorder_id):
    query="Call receive_reorder(%s)"
    params=(reorder_id,)
    cursor.execute(query,params)
    conn.commit()

def find_reorder_id_details(cursor):
    query="Select r.reorder_id,r.product_id,p.product_name from reorders r left join products p on r.product_id=p.product_id"
    cursor.execute(query)
    rows=cursor.fetchall()
    return rows
# conn=connect_to_db()
# cursor=conn.cursor(dictionary=True)
# print(products_history(cursor,123))
