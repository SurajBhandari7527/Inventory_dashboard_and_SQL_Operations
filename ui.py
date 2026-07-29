import streamlit as st
import pandas as pd
from backend_database import (
    basic_data,
    connect_to_db,
    get_table_details,
    find_unique_categories,
    find_unique_suppliers,
    add_new_product_id,
    product_status,
    products_stock_history,
    products_shipment_history,
    find_all_products,
    place_reorder,
    find_reorder_id_details,
    receive_reorder
)

st.sidebar.title("Inventory Management Dashboard")
st.markdown("<h1 style='font-size:35px;'>Inventory and Supply Chain Dashboard</h1>", unsafe_allow_html=True)
option=st.sidebar.radio("Select option:", ["Basic Information", "Operational Task"])

conn=connect_to_db()
cursor=conn.cursor(dictionary=True)


#-----------------Basic Info Part----------
if option=="Basic Information":
    st.header("Basic Metrics")
    basic_info=basic_data(cursor)

    cols=st.columns(3)
    keys=list(basic_info.keys())

    for i in range(3):
        cols[i].metric(keys[i],basic_info[keys[i]])

    cols=st.columns(3)
    for i in range(3,6):
        cols[i-3].metric(keys[i],basic_info[keys[i]])

    #get table details
    table_details=get_table_details(cursor)
    #supplier contact details
    st.divider()
    for i in table_details:
        df=pd.DataFrame(table_details[i])
        st.header(i)
        st.dataframe(df)
        st.divider()

if option=="Operational Task":
    st.header("Operational Tasks")
    operation_option=st.selectbox("Choose a task",["Add new Product" , "Product History", "Place Reorder", "Receive Reorder"])
    if operation_option=="Add new Product":
        with st.form("Add product form"):
            product_name=st.text_input("Product Name")
            categories=find_unique_categories(cursor)
            category=st.selectbox("Category",categories)

            suppliers=find_unique_suppliers(cursor)   
            supplier_names=[x['supplier_name'] for x in suppliers]
            supplier_id=[x['supplier_id'] for x in suppliers]

            supplier=st.selectbox("Supplier",options=supplier_id, format_func=lambda x: supplier_names[supplier_id.index(x)])
            price=st.number_input("Price",min_value=0.00)
            quantity=st.number_input("Stock Quantity",min_value=1, step=1)
            reorder=st.number_input("Reorder Level",min_value=0, step=1)

            btn=st.form_submit_button("Add Product")
            if btn:
                if not product_name:
                    st.error("Please enter the product name")
                if price==0.00:
                    st.error("Please check the price of the product")
                try:
                    add_new_product_id(cursor,conn,product_name,category,price,quantity,reorder,supplier)
                    st.success("Successfully added a new product")
                except Exception as e:
                 st.error(f"Exception occured: {e}")

    elif operation_option=="Product History":
        result=find_all_products(cursor)
        product_ids=[d['product_id'] for d in result]
        product_names=[str(d['product_id'])+"-"+d['product_name'] for d in result]

        product_id=st.selectbox("Choose the product: (Format:ProductID-ProductName)",options=product_ids, format_func=lambda x: product_names[product_ids.index(x)])
        btn=st.button("Find details") 
        if btn:
            product_details=product_status(cursor,product_id=product_id)
            # st.text(product_details)
            cols=st.columns(3)
            cols[0].metric("Product id",f"{product_details[0]["product_id"]}")
            cols[1].metric("Current stock quantity",product_details[0]["stock_quantity"])
            cols[2].metric("Reorder level",product_details[0]["reorder_level"])
            cols=st.columns(3)
            cols[0].metric("Supplier id", product_details[0]["supplier_id"])
            cols[1].metric("Supplier name",product_details[0]["supplier_name"])
            needs_reorder=product_details[0]["stock_quantity"]<product_details[0]["reorder_level"]
            if needs_reorder:
                reorder="Yes"
            else:
                reorder="No"

            cols[2].metric("Needs Reorder?",reorder )
            st.divider()
            st.header("Products history stock details")
            history_details=products_stock_history(cursor,product_id)
            df=pd.DataFrame(history_details)
            st.dataframe(df)

            st.divider()
            st.header("Products history shipment details")
            history_details=products_shipment_history(cursor,product_id,filter=False)
            df=pd.DataFrame(history_details)
            st.dataframe(df)

    elif operation_option=="Place Reorder":

        result=find_all_products(cursor)
        product_ids=[d['product_id'] for d in result]
        product_names=[str(d['product_id'])+"-"+d['product_name'] for d in result]
        with st.form("Choose product and quantity"):
            product_id=st.selectbox("Choose the product: (Format:ProductID-ProductName)",options=product_ids, format_func=lambda x: product_names[product_ids.index(x)])
            quantity=st.number_input("Enter the quantity",min_value=1, step=1)
            btn=st.form_submit_button("Place reorder") 

        if btn:
            try:
                place_reorder(cursor,conn,product_id,quantity)
                st.success("Reorder success. You can look at the products history")
            except Exception as e:
                st.error(f"Exception occured as {e}")

    elif operation_option=="Receive Reorder":
        result=find_reorder_id_details(cursor)
        reorder_ids=[d['reorder_id'] for d in result]
        product_names=[str(d['product_id'])+"-"+d['product_name'] for d in result]
        product_ids=[d['product_id'] for d in result]

        reorder_id=st.selectbox("Choose the product: (Format:ProductID-ProductName)",options=reorder_ids, format_func=lambda x: product_names[reorder_ids.index(x)])
        btn=st.button("Receive reorder") 
        idx=reorder_ids.index(reorder_id)
        product_id=product_ids[idx]
        st.divider()
        st.header("Products orders details")
        history_details=products_shipment_history(cursor,product_id,filter=True)
        df=pd.DataFrame(history_details)
        if not history_details:
            st.warning("No order placed")
        else:
            st.dataframe(df)

        if btn:
            try: 
                receive_reorder(cursor,conn,reorder_id)
                st.success("Successfully received reorder")
            except Exception as e:
                st.error(f"Exception occured: {e}")
            

        
            




    
