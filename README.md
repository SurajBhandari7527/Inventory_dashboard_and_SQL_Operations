# 📦 Inventory and Supply Chain Management Dashboard

An interactive, data-driven web application designed to manage inventory, track product history, and streamline supply chain operations in real time. Built using **Python**, **Streamlit**, and **MySQL**, this application provides key operational metrics, automated inventory threshold tracking, and manual reorder controls.

Demo Video:
<img width="800" height="500" alt="inventory (1)" src="https://github.com/user-attachments/assets/963e444e-49d1-4bc1-b569-21697a18c30c" />
---


# Try now: https://inventorydashboardandsqloperations.streamlit.app/



## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Architecture](#-project-architecture)
- [Database Schema & Stored Procedures](#-database-schema--stored-procedures)
- [Installation & Setup](#-installation--setup)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [Component Breakdown](#-component-breakdown)

---

## ✨ Features

### 📊 1. Basic Information Dashboard
* **Key Performance Metrics (KPIs):**
  * Total Suppliers count.
  * Total Products in stock.
  * Total Categories dealing.
  * Total Sales Value in the last 3 months.
  * Total Restock Value in the last 3 months.
  * Products below reorder threshold (with no pending orders).
* **Interactive Data Tables:**
  * Detailed supplier contact directory.
  * Overall product stock details and supplier links.
  * Filtered view for products needing urgent reordering.

### ⚙️ 2. Operational Tasks
* **Add New Product:** Interface to add products directly into the database with category, supplier, stock, price, and reorder thresholds.
* **Product History & Analytics:** 
  * View current stock status, supplier info, and reorder status for any chosen product.
  * Historical log of stock adjustments (`stock_entries`).
  * Full shipment and order lifecycle history (`reorders` & `shipments`).
* **Place Reorder:** Send new purchase/reorder requests for products reaching low stock levels.
* **Receive Reorder:** Process incoming reorders to automatically update database stock levels via stored database procedures.

---

## 🛠️ Tech Stack

* **Frontend / UI:** [Streamlit](https://streamlit.io/)
* **Data Processing:** [Pandas](https://pandas.pydata.org/)
* **Database:** [MySQL Database Server](https://www.mysql.com/)
* **Database Connector:** `mysql-connector-python`
* **Language:** Python 3.14

---

## 📁 Project Architecture

```text
├── backend_database.py   # Handles database connections, queries, and stored procedure calls
├── ui.py                 # Streamlit frontend application code & dashboard layout
└── README.md             # Project documentation
└── requirements.txt             # all dependencies
```

---

## 🗄️ Database Schema & Stored Procedures

To ensure full compatibility with this application, your MySQL database requires the following tables and procedures:

### Core Tables
1. **`products`**: `product_id`, `product_name`, `category`, `price`, `stock_quantity`, `reorder_level`, `supplier_id`
2. **`suppliers`**: `supplier_id`, `supplier_name`, `contact_name`, `email`, `phone`
3. **`stock_entries`**: `entry_id`, `product_id`, `change_quantity`, `change_type`, `price`, `entry_date`
4. **`reorders`**: `reorder_id`, `product_id`, `reorder_quantity`, `reorder_date`, `status`
5. **`shipments`**: `shipment_id`, `product_id`, `quantity_received`, `shipment_date`

### Stored Procedures Required
* **`AddNewProductManualID(...)`**: Handles inserting a new product entry into the system.
* **`receive_reorder(reorder_id)`**: Handles changing the reorder status to "Received" and updating the stock quantity in the `products` table.

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.8 or higher installed on your system.
* Running MySQL Server instance with the backend database imported.

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install streamlit mysql-connector-python pandas
```

---

## ⚙️ Configuration

Set up your database connection using Streamlit's secrets management tool.

Create a directory `.streamlit` in the root folder and add a `secrets.toml` file inside it:

```toml
# .streamlit/secrets.toml

[mysql]
host = "localhost"
user = "your_mysql_user"
password = "your_mysql_password"
database = "your_database_name"
port = 3306
```

---

## 🏃 Usage Guide

Run the Streamlit application using:

```bash
streamlit run ui.py
```

Open your browser at `http://localhost:8501` to view the app.

---

## 🧩 Component Breakdown

### 1. `backend_database.py` (Database Controller)
Contains Python functions executing SQL queries and calling stored procedures using `mysql.connector`.
* **`connect_to_db()`**: Establishes connection using parameters stored in `.streamlit/secrets.toml`.
* **`basic_data(cursor)`**: Runs aggregation metrics query to generate aggregate stats for the basic dashboard.
* **`get_table_details(cursor)`**: Queries information for supplier details, product stock overview, and low-stock products.
* **`add_new_product_id(...)`**: Invokes the `AddNewProductManualID` stored procedure to safely add new products.
* **`products_stock_history(...)`**: Fetches granular log entries regarding stock additions and deductions.
* **`products_shipment_history(...)`**: Unifies order logs and receiving records via database `UNION` queries.
* **`place_reorder(...)` & `receive_reorder(...)`**: Manages operational supply orders and executes stock updating procedures.

### 2. `ui.py` (Frontend Application)
Renders UI components dynamically via Streamlit.
* **Sidebar Navigation:** Allows switching between **Basic Information** and **Operational Task** views.
* **Metrics Cards:** Renders clean numerical blocks (`st.metric`) to highlight aggregate backend stats.
* **Dynamic Forms:** Provides inputs (`st.text_input`, `st.selectbox`, `st.number_input`) to add products or create purchase orders.
* **Data Frames:** Displays Pandas dataframes generated directly from dynamic SQL dictionary objects.
---

---

```
