import joblib
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import SCALER_PATH, ENCODER_PATH, XGB_MODEL_PATH, FEATURES


try:
    scaler = joblib.load(SCALER_PATH)
    encoder = joblib.load(ENCODER_PATH)
    model = joblib.load(XGB_MODEL_PATH) 
except Exception as e:
    print(f"Warning: Model assets not found. Run preprocess.py and train.py first. ({e})")

def predict_next_hour_risk(live_data_dict):
    """
    Expects a dictionary with the 6 pollutant values.
    Returns the predicted Health Risk string.
    """
    input_df = pd.DataFrame([live_data_dict])[FEATURES]
    
  
    input_scaled = scaler.transform(input_df)
    
    
    prediction_encoded = model.predict(input_scaled)
    

    predicted_risk = encoder.inverse_transform(prediction_encoded)[0]
    
    return predicted_risk

if __name__ == "__main__":
  
    test_live_data = {
        "PM10 (µg/m³)": 85.5,
        "PM2.5 (µg/m³)": 45.2,
        "CO (µg/m³)": 800.0,
        "NO2 (µg/m³)": 25.1,
        "SO2 (µg/m³)": 10.5,
        "O3 (µg/m³)": 40.0
    }
    result = predict_next_hour_risk(test_live_data)
    print(f"Predicted Next Hour Risk: {result}")