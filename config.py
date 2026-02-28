import os

# Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data Paths
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "India_Extended_Historical_AQI_2Years.csv")
PROCESSED_DATA_X = os.path.join(BASE_DIR, "data", "processed", "X_processed.csv")
PROCESSED_DATA_Y = os.path.join(BASE_DIR, "data", "processed", "y_processed.csv")

# Model Paths
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "models", "label_encoder.pkl")
RF_MODEL_PATH = os.path.join(BASE_DIR, "models", "random_forest_model.pkl")
XGB_MODEL_PATH = os.path.join(BASE_DIR, "models", "xgboost_model.pkl")

# Features expected by the model
FEATURES = [
    "PM10 (µg/m³)", "PM2.5 (µg/m³)", "CO (µg/m³)", 
    "NO2 (µg/m³)", "SO2 (µg/m³)", "O3 (µg/m³)"
]