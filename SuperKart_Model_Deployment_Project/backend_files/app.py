# Flask backend that loads the serialized SuperKart sales-forecasting model
# and exposes a /predict endpoint for scoring new records

import joblib
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# loading the trained pipeline (preprocessing + model) saved from the notebook
model = joblib.load("superkart_sales_model.joblib")


@app.route("/", methods=["GET"])
def home():
    return "SuperKart Sales Forecasting API is up and running."


@app.route("/predict", methods=["POST"])
def predict():
    """
    Expects a JSON payload with either:
      - a single record: {"Product_Weight": 12.66, "Product_Sugar_Content": "Low Sugar", ...}
      - a list of records: [{...}, {...}]
    Returns predicted Product_Store_Sales_Total for each record.
    """
    payload = request.get_json()

    if isinstance(payload, dict):
        records = [payload]
    else:
        records = payload

    input_df = pd.DataFrame(records)

    predictions = model.predict(input_df)

    return jsonify({"predictions": predictions.tolist()})


if __name__ == "__main__":
    # host=0.0.0.0 so the app is reachable when the port is forwarded from a Codespace
    app.run(host="0.0.0.0", port=5000, debug=False)
