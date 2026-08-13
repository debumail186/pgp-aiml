# Streamlit frontend for the SuperKart sales-forecasting model.
# Collects product/store attributes from the user and calls the Flask backend's
# /predict endpoint to return the forecasted Product_Store_Sales_Total.

import streamlit as st
import requests

# URL of the Flask backend running in the same Codespace (forwarded port)
BACKEND_URL = "http://localhost:5000/predict"

st.set_page_config(page_title="SuperKart Sales Forecasting", layout="centered")

st.title("SuperKart Sales Forecasting")
st.write(
    "Enter the product and store attributes below to forecast the quarterly sales "
    "revenue (Product_Store_Sales_Total) for that product-store combination."
)

with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        product_weight = st.number_input("Product Weight", min_value=0.0, value=12.5, step=0.1)
        product_sugar_content = st.selectbox(
            "Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"]
        )
        product_allocated_area = st.slider(
            "Product Allocated Area (ratio of store display area)", 0.0, 0.3, 0.05, step=0.01
        )
        product_type = st.selectbox(
            "Product Type",
            [
                "Frozen Foods", "Dairy", "Canned", "Baking Goods", "Health and Hygiene",
                "Snack Foods", "Meat", "Household", "Hard Drinks", "Fruits and Vegetables",
                "Breads", "Soft Drinks", "Breakfast", "Others", "Starchy Foods", "Seafood",
            ],
        )
        product_category = st.selectbox("Product Category", ["Food", "Drinks", "Non-Consumable"])

    with col2:
        product_mrp = st.number_input("Product MRP", min_value=0.0, value=140.0, step=1.0)
        store_size = st.selectbox("Store Size", ["High", "Medium", "Small"])
        store_location_city_type = st.selectbox(
            "Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"]
        )
        store_type = st.selectbox(
            "Store Type",
            ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"],
        )
        store_age = st.number_input("Store Age (years)", min_value=0, value=10, step=1)

    submitted = st.form_submit_button("Forecast Sales")

if submitted:
    payload = {
        "Product_Weight": product_weight,
        "Product_Sugar_Content": product_sugar_content,
        "Product_Allocated_Area": product_allocated_area,
        "Product_Type": product_type,
        "Product_MRP": product_mrp,
        "Store_Size": store_size,
        "Store_Location_City_Type": store_location_city_type,
        "Store_Type": store_type,
        "Store_Age": store_age,
        "Product_Category": product_category,
    }

    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=10)
        response.raise_for_status()
        prediction = response.json()["predictions"][0]
        st.success(f"Forecasted Sales Revenue: {prediction:,.2f}")
    except Exception as e:
        st.error(f"Could not reach the backend. Make sure it is running. Details: {e}")
