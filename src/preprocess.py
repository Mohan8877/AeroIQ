import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler, LabelEncoder
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import RAW_DATA_PATH, PROCESSED_DATA_X, PROCESSED_DATA_Y, SCALER_PATH, ENCODER_PATH, FEATURES

def categorize_aqi(aqi):
    """Convert numerical AQI into Health Risk Categories"""
    if pd.isna(aqi): return "Unknown" 
    if aqi <= 50: return "Good"
    elif aqi <= 100: return "Moderate"
    elif aqi <= 150: return "Unhealthy for Sensitive"
    elif aqi <= 200: return "Unhealthy"
    elif aqi <= 300: return "Very Unhealthy"
    else: return "Hazardous"

def run_preprocessing():
    print("Loading raw data...")
    df = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    
   
    print("Cleaning mixed data types...")
    for col in FEATURES + ['Calculated AQI']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 1. Sort by City and Date to ensure correct time sequence
    df = df.sort_values(by=['City', 'Date'])
    
    # 2. CREATE THE TARGET: Next Hour's AQI
    print("Creating next-hour target variables...")
    df['Next_Hour_AQI'] = df.groupby('City')['Calculated AQI'].shift(-1)
    
    # Drop the last hour for each city since we don't know the "next hour" yet
    df = df.dropna(subset=['Next_Hour_AQI'])
    
    # 3. Create Categorical Health Risk for the Next Hour
    df['Next_Hour_Risk'] = df['Next_Hour_AQI'].apply(categorize_aqi)
    
    # 4. Extract Features (X) and Target (y)
    X = df[FEATURES].copy()
    y = df['Next_Hour_Risk']
    
    # Fill any missing pollutant data with the median
    # This will now work perfectly because X is 100% numeric
    X = X.fillna(X.median())
    
    # 5. Scale the Features (Important for ML)
    print("Scaling features and encoding labels...")
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=FEATURES)
    
    # Ensure the models directory exists
    os.makedirs(os.path.dirname(SCALER_PATH), exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)
    
    # 6. Encode the Target Labels (e.g., 'Good' -> 0, 'Hazardous' -> 1)
    encoder = LabelEncoder()
    y_encoded = pd.Series(encoder.fit_transform(y), name="Risk_Label")
    joblib.dump(encoder, ENCODER_PATH)
    
    # 7. Save processed data for training
    os.makedirs(os.path.dirname(PROCESSED_DATA_X), exist_ok=True)
    X_scaled.to_csv(PROCESSED_DATA_X, index=False)
    y_encoded.to_csv(PROCESSED_DATA_Y, index=False)
    
    print(f"✅ Preprocessing complete. Scaler and Encoder saved to /models.")

if __name__ == "__main__":
    run_preprocessing()