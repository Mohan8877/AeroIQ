# 🌍 Air Pollution Health Risk Prediction  
### A Machine Learning–Driven Environmental Health Intelligence System

---

## 📌 Overview

**Air Pollution Health Risk Prediction** is an intelligent environmental monitoring system designed to forecast air quality risks and provide personalized health-based recommendations.

Unlike traditional AQI dashboards that only display current values, this system:

- Predicts next-hour AQI category using machine learning
- Identifies the primary toxic pollutant
- Adjusts risk levels based on user health conditions
- Provides preventive medical guidance

The goal is to enable proactive healthcare decisions before exposure occurs.

---

## 🚑 Real-World Significance

Air pollution contributes to:

- Asthma exacerbations
- COPD flare-ups
- Cardiovascular stress
- Respiratory inflammation
- Hypoxia (CO exposure)

This system helps vulnerable populations by:

- Predicting risk before it peaks
- Customizing warnings for chronic patients
- Reducing emergency hospital visits
- Supporting preventive respiratory care

---

## 🏗 System Architecture

```
User (Browser)
      ↓
Flask Backend
      ↓
In-Memory Cache (TTL: 10 min)
      ↓
External APIs (Air Quality + Geocoding)
      ↓
ML Prediction Engine
      ↓
Health Risk Expert System
      ↓
Dynamic UI & Clinical Recommendations
```

---

## ⚙ Technology Stack

### 🔹 Frontend
- HTML5 / CSS3
- Tailwind-based Dark Mode UI
- Vanilla JavaScript (ES6)
- Chart.js (12-hour spline forecast visualization)

### 🔹 Backend
- Python 3
- Flask (Micro Web Framework)
- Waitress (Production WSGI Server)

### 🔹 Database
- SQLite3 (User health profile logging)

### 🔹 Machine Learning
- XGBoost Regressor
- Random Forest Regressor
- StandardScaler
- LabelEncoder

---

## 📡 Data Acquisition Pipeline

### APIs Used

- Open-Meteo Air Quality API  
- Open-Meteo Geocoding API  
- Nominatim (OpenStreetMap)

### Environmental Variables Monitored

- PM2.5
- PM10
- CO
- NO₂
- SO₂
- O₃
- Temperature
- Humidity
- Time of Day

### Caching Strategy

- In-memory RAM caching
- Time-to-Live: 10 minutes
- Prevents redundant API calls
- Supports high concurrent users

---

## 📊 AQI Calculation Method

The Air Quality Index (AQI) is calculated using the US EPA breakpoint formula:

```
I_p = ((I_Hi - I_Lo) / (BP_Hi - BP_Lo)) * (C_p - BP_Lo) + I_Lo
```

Where:
- C_p = Pollutant concentration
- BP_Hi / BP_Lo = Breakpoints
- I_Hi / I_Lo = AQI index bounds

Final AQI = Maximum pollutant index value.

---

## 🤖 Machine Learning Prediction Model

### 🎯 Target

Predict AQI Category at time (t + 1 hour).

### 📦 Features

- Current pollutant concentrations
- Weather conditions
- Time encoding

### 🏗 Model Selection

Tree-based ensemble methods were used because:

- Environmental data is highly non-linear
- Pollutants interact dynamically
- Sudden spikes require branch-based decision modeling

Models implemented:

- Random Forest Regressor
- XGBoost Regressor

### 🔬 Training Strategy

- 80% Training Data
- 20% Testing Data
- Feature normalization using StandardScaler
- Performance evaluated using confusion matrices

---

## 🧠 Health Risk Expert System

The core innovation is the dynamic health-based recommendation engine.

### 🔹 Base Risk Calculation

Scales AQI (0–300) into a 0–100% danger index.

### 🔹 Vulnerability Multiplier

If user declares a chronic condition:

- Asthma → 1.3× risk multiplier
- COPD → 1.4× risk multiplier

### 🔹 Scenario-Based Output

| Condition | Risk | Pollutant | Recommendation |
|------------|------|------------|----------------|
| Normal | Moderate | PM2.5 | Ventilate room |
| Asthma | Moderate | O₃ | Stay indoors, keep inhaler ready |
| Cardiac | High | CO | Avoid outdoor exposure |

---

## 📂 Project Structure

```
Air_Pollution_Health_Risk_Prediction/
│
├── app.py
├── config.py
├── check_db.py
├── aeroiq_database.db
│
├── models/
│   ├── random_forest_model.pkl
│   ├── xgboost_model.pkl
│   ├── scaler.pkl
│   └── label_encoder.pkl
│
├── src/
│   ├── api_fetch.py
│   ├── preprocess.py
│   ├── predict.py
│   ├── train.py
│   └── evaluate.py
│
├── templates/
├── static/
├── requirements.txt
└── README.md
```

---

## 🛠 Installation & Setup

### 1️⃣ Clone Repository

```
git clone https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git
cd REPOSITORY_NAME
```

### 2️⃣ Create Virtual Environment

```
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

## ▶ Running the Application

### Development Mode

```
python app.py
```

### Production Mode (Recommended)

```
pip install waitress
waitress-serve --port=8000 app:app
```

Access:
```
http://localhost:8000
```

---

## 🚀 Deployment Recommendation

### Recommended Production Setup

Frontend → Vercel  
Backend → Render  
Database → SQLite (PostgreSQL optional upgrade)

Build Command:
```
pip install -r requirements.txt
```

Start Command:
```
gunicorn app:app
```

---

## 🔮 Future Enhancements

- Mobile Application Version
- SMS Health Alerts
- Push Notifications
- Docker Containerization
- PostgreSQL Migration
- Real-time Geo-fencing Alerts
- Public REST API Version

---

## 👨‍💻 Author

TEAM-Code Crusaders
---

## ⭐ Final Statement

Air Pollution Health Risk Prediction transforms environmental monitoring into predictive, personalized respiratory intelligence — enabling preventive healthcare through machine learning.
