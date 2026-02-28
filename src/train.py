'''import pandas as pd
import joblib
import sys
import os
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import PROCESSED_DATA_X, PROCESSED_DATA_Y, RF_MODEL_PATH, XGB_MODEL_PATH

def train_models():
    print("Loading processed data...")
    X = pd.read_csv(PROCESSED_DATA_X)
    y = pd.read_csv(PROCESSED_DATA_Y)['Risk_Label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    print(f"Random Forest Accuracy: {accuracy_score(y_test, rf_preds):.4f}")
    joblib.dump(rf_model, RF_MODEL_PATH)
    
    # Train XGBoost
    print("Training XGBoost...")
    xgb_model = XGBClassifier(eval_metric='mlogloss', random_state=42)
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    print(f"XGBoost Accuracy: {accuracy_score(y_test, xgb_preds):.4f}")
    joblib.dump(xgb_model, XGB_MODEL_PATH)
    
    print("✅ Models successfully trained and saved to /models.")

if __name__ == "__main__":
    train_models()'''


import pandas as pd
import joblib
import sys
import os
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import PROCESSED_DATA_X, PROCESSED_DATA_Y, RF_MODEL_PATH, XGB_MODEL_PATH

def get_file_size_mb(filepath):
    """Helper function to check file size in Megabytes."""
    return os.path.getsize(filepath) / (1024 * 1024)

def train_models():
    print("Loading processed data...")
    X = pd.read_csv(PROCESSED_DATA_X)
    y = pd.read_csv(PROCESSED_DATA_Y)['Risk_Label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # ---------------------------------------------------------
    # 1. Train Random Forest (DEPLOYMENT SAFE)
    # ---------------------------------------------------------
    print("Training Random Forest...")
    # ADDED: max_depth and min_samples_split to prevent 1GB+ bloat!
    rf_model = RandomForestClassifier(
        n_estimators=40,       # Reduced from 50 to keep it very light
        max_depth=12,          # CRITICAL: Stops trees from growing infinitely
        min_samples_split=5,   # Prunes unnecessary branches
        random_state=42, 
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    print(f"Random Forest Accuracy: {accuracy_score(y_test, rf_preds):.4f}")
    
    joblib.dump(rf_model, RF_MODEL_PATH)
    print(f" -> RF Model saved. Size: {get_file_size_mb(RF_MODEL_PATH):.2f} MB")
    
    # ---------------------------------------------------------
    # 2. Train XGBoost
    # ---------------------------------------------------------
    print("\nTraining XGBoost...")
    # ADDED: max_depth to ensure this also stays incredibly small
    xgb_model = XGBClassifier(
        max_depth=6,           # XGBoost standard depth
        learning_rate=0.1,
        n_estimators=50,
        eval_metric='mlogloss', 
        random_state=42
    )
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    print(f"XGBoost Accuracy: {accuracy_score(y_test, xgb_preds):.4f}")
    
    joblib.dump(xgb_model, XGB_MODEL_PATH)
    print(f" -> XGBoost Model saved. Size: {get_file_size_mb(XGB_MODEL_PATH):.2f} MB")
    
    print("\n✅ Models successfully trained and are safe for GitHub/Render deployment!")

if __name__ == "__main__":
    train_models()