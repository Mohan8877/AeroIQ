import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import PROCESSED_DATA_X, PROCESSED_DATA_Y, RF_MODEL_PATH, XGB_MODEL_PATH, ENCODER_PATH, BASE_DIR

def evaluate_models():
    print("Loading data and models...")
    X = pd.read_csv(PROCESSED_DATA_X)
    y = pd.read_csv(PROCESSED_DATA_Y)['Risk_Label']
    
    # Recreate the exact same test set used in training
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    rf_model = joblib.load(RF_MODEL_PATH)
    xgb_model = joblib.load(XGB_MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    
    # Get the actual class names (Good, Moderate, etc.) in the correct order
    class_names = encoder.classes_
    
    # --- Evaluate Random Forest ---
    print("\n" + "="*40)
    print("RANDOM FOREST EVALUATION")
    print("="*40)
    rf_preds = rf_model.predict(X_test)
    print(classification_report(y_test, rf_preds, target_names=class_names))
    save_confusion_matrix(y_test, rf_preds, class_names, "Random Forest", "random_forest_confusion_matrix.png")

    # --- Evaluate XGBoost ---
    print("\n" + "="*40)
    print("XGBOOST EVALUATION")
    print("="*40)
    xgb_preds = xgb_model.predict(X_test)
    print(classification_report(y_test, xgb_preds, target_names=class_names))
    save_confusion_matrix(y_test, xgb_preds, class_names, "XGBoost", "xgboost_confusion_matrix.png")

def save_confusion_matrix(y_true, y_pred, class_names, model_name, filename):
    """Generates and saves a confusion matrix heatmap image."""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title(f'{model_name} Confusion Matrix')
    plt.ylabel('Actual Risk')
    plt.xlabel('Predicted Risk')
    plt.tight_layout()
    
    # Save to the static folder
    save_path = os.path.join(BASE_DIR, "static", filename)
    plt.savefig(save_path)
    plt.close()
    print(f"✅ Saved confusion matrix to {save_path}")

if __name__ == "__main__":
    evaluate_models()