# Streamlit frontend for the SuperKart sales-forecasting model.
# Supports two modes:
#   1. Single record - fill in a form, get one forecast back
#   2. Batch - upload a CSV of records, get a forecast column added and a download link
# Both modes call the Flask backend's /predict endpoint, which already accepts either
# a single JSON object or a list of JSON objects.

import io

import pandas as pd
import requests
import streamlit as st

# URL of the Flask backend running in the same Codespace (forwarded port)
BACKEND_URL = "http://localhost:5000/predict"

st.set_page_config(page_title="SuperKart Sales Forecasting", layout="centered")

st.title("SuperKart Sales Forecasting")

mode = st.radio("Choose input mode", ["Single record", "Batch (CSV upload)"], horizontal=True)

REQUIRED_COLUMNS = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_Type",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Store_Age",
    "Product_Category",
]

# ---------------------------------------------------------------------------
# Mode 1: Single record
# ---------------------------------------------------------------------------
if mode == "Single record":
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

# ---------------------------------------------------------------------------
# Mode 2: Batch CSV upload
# ---------------------------------------------------------------------------
else:
    st.write(
        "Upload a CSV containing one row per product-store combination you want to forecast. "
        "The file must include the following columns (extra columns, e.g. an existing "
        "`Product_Store_Sales_Total`, are ignored):"
    )
    st.code(", ".join(REQUIRED_COLUMNS))

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            batch_df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Could not read the CSV file: {e}")
            batch_df = None

        if batch_df is not None:
            missing = [c for c in REQUIRED_COLUMNS if c not in batch_df.columns]
            if missing:
                st.error(f"The uploaded file is missing required column(s): {missing}")
            else:
                st.write(f"Loaded {len(batch_df)} rows. Preview:")
                st.dataframe(batch_df.head())

                if st.button("Forecast Sales for Uploaded File"):
                    # keep only the columns the model expects, in a stable order
                    records = batch_df[REQUIRED_COLUMNS].to_dict(orient="records")

                    try:
                        response = requests.post(BACKEND_URL, json=records, timeout=30)
                        response.raise_for_status()
                        predictions = response.json()["predictions"]

                        result_df = batch_df.copy()
                        result_df["Predicted_Product_Store_Sales_Total"] = predictions

                        st.success(f"Generated forecasts for {len(result_df)} rows.")
                        st.dataframe(result_df)

                        csv_buffer = io.StringIO()
                        result_df.to_csv(csv_buffer, index=False)
                        st.download_button(
                            label="Download results as CSV",
                            data=csv_buffer.getvalue(),
                            file_name="superkart_sales_forecast.csv",
                            mime="text/csv",
                        )
                    except Exception as e:
                        st.error(f"Could not reach the backend. Make sure it is running. Details: {e}")
