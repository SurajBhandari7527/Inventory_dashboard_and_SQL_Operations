import streamlit as st

# Sample data
products = ["Groceries", "Clothing", "Toys", "Furniture", "Electronics"]

# Search box
search_query = st.text_input("Search for a product")

# Filter results
if search_query:
    results = [p for p in products if search_query.lower() in p.lower()]
else:
    results = products

st.write("Results:", results)
