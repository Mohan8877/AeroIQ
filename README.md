# 🌍 AeroIQ  
### Proactive Environmental Health Intelligence Platform

> A machine learning–powered respiratory risk prediction system that forecasts next-hour AQI and delivers personalized clinical-grade recommendations.

---

## 📌 Table of Contents

- [1. Project Vision](#-1-project-vision)
- [2. Real-World Impact](#-2-real-world-impact)
- [3. System Architecture](#-3-system-architecture)
- [4. Technology Stack](#-4-technology-stack)
- [5. Data Pipeline](#-5-data-pipeline)
- [6. AQI Calculation Methodology](#-6-aqi-calculation-methodology)
- [7. Machine Learning Pipeline](#-7-machine-learning-pipeline)
- [8. Intelligent Health Engine](#-8-intelligent-health-engine)
- [9. Project Structure](#-9-project-structure)
- [10. Installation & Setup](#-10-installation--setup)
- [11. Running the Application](#-11-running-the-application)
- [12. Deployment Guide](#-12-deployment-guide)
- [13. Future Enhancements](#-13-future-enhancements)

---

# 🧠 1. Project Vision

AeroIQ is not a weather dashboard.

It is a **predictive respiratory intelligence system** that:

- Forecasts AQI risk 1 hour ahead
- Adjusts health guidance per patient condition
- Identifies primary toxic pollutant
- Reduces emergency exacerbations

The platform combines:
- Real-time environmental APIs
- Time-series machine learning
- Rule-based clinical decision engine
- High-speed in-memory caching

---

# 🚑 2. Real-World Impact

### 🔹 Preventative Healthcare
- Early warnings for asthma/COPD patients
- Reduced ER visits
- Proactive medication timing

### 🔹 Precision Risk Modeling
A "Moderate AQI" means:
- Safe for healthy adult
- Dangerous for elderly COPD patient

AeroIQ modifies:
- UI theme
- Risk calculation
- Health recommendations

Based on user condition.

### 🔹 Resource Optimization
By preventing severe flare-ups:
- Lowers healthcare burden
- Encourages preventive planning

---

# 🏗 3. System Architecture

```
User (Browser)
      ↓
Flask Backend
      ↓
API Cache (RAM)
      ↓
Open-Meteo APIs
      ↓
ML Prediction Engine
      ↓
Expert Health System
      ↓
Dynamic UI Response
```

Concurrent users handled using:
- Waitress WSGI server
- Thread multiplexing
- In-memory caching (TTL: 10 minutes)

---

# ⚙ 4. Technology Stack

## 🔹 Frontend
- HTML5 / CSS3
- Tailwind Dark Mode UI
- Vanilla JavaScript (ES6)
- Chart.js (12-hour spline forecast graphs)

## 🔹 Backend
- Python 3
- Flask (Routing & Templating)
- Waitress (Production WSGI Server)

## 🔹 Database
- SQLite3 (User profiles & analytics logging)

## 🔹 Machine Learning
- XGBoost Regressor
- Random Forest Regressor
- StandardScaler
- LabelEncoder

---

# 🌐 5. Data Pipeline

### APIs Used

- Open-Meteo Air Quality API
- Open-Meteo Geocoding API
- Nominatim (OpenStreetMap)

### Features Extracted

- PM2.5
- PM10
- NO2
- CO
- SO2
- O3
- Temperature
- Humidity
- Time of Day

### RAM Caching Strategy

If 50 users query same city:
- 1 external API request
- 49 served from memory

TTL: 10 minutes

---

# 📊 6. AQI Calculation Methodology

AeroIQ implements the US EPA breakpoint formula:

```
I_p = ((I_Hi - I_Lo) / (BP_Hi - BP_Lo)) * (C_p - BP_Lo) + I_Lo
```

Where:
- C_p = pollutant concentration
- BP_Hi / BP_Lo = breakpoints
- I_Hi / I_Lo = AQI range bounds

Final AQI = maximum pollutant index.

---

# 🤖 7. Machine Learning Pipeline

## 🎯 Target
Predict AQI category at t + 1 hour.

## 📦 Feature Engineering
- Pollutant values at time t
- Weather variables
- Time encoding

## 🏗 Model Choice
Tree-based ensemble models chosen because:
- Environmental data is non-linear
- Gas interactions are complex
- Sudden spikes require branch-based logic

## 🔬 Training Process
- 80% Training
- 20% Testing
- Feature normalization
- Evaluation using confusion matrices

---

# 🧠 8. Intelligent Health Engine

### 🔹 Base Danger Index
Scales AQI (0–300) → 0–100% risk

### 🔹 Vulnerability Multiplier
Asthma → 1.3x  
COPD → 1.4x  

### 🔹 Example Scenarios

| Condition | Risk | Gas | Output |
|------------|------|-----|--------|
| Normal | Moderate | PM2.5 | Ventilate room |
| Asthma | Moderate | O3 | Stay indoors |

---

# 📂 9. Project Structure

```
AeroIQ/
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

# 🛠 10. Installation & Setup

## 🔹 Step 1: Clone Repository

```
git clone https://github.com/YOUR_USERNAME/AeroIQ.git
cd AeroIQ
```

## 🔹 Step 2: Create Virtual Environment

```
python3 -m venv venv
source venv/bin/activate
```

## 🔹 Step 3: Install Dependencies

```
pip install -r requirements.txt
```

---

# ▶ 11. Running the Application

## Development Mode

```
python app.py
```

## Production Mode (Recommended)

```
pip install waitress
waitress-serve --port=8000 app:app
```

Access:
```
http://localhost:8000
```

---

# 🚀 12. Deployment Guide

## Recommended Architecture

Frontend → Vercel  
Backend → Render  
Database → SQLite (or PostgreSQL in future)

### Render Setup
- Connect GitHub repo
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

---

# 🔮 13. Future Enhancements

- Mobile app integration
- SMS health alerts
- Push notifications
- Geo-fenced respiratory warnings
- PostgreSQL migration
- Docker containerization
- Public API release

---

# 👨‍💻 Author

TEAM-Code Crusaders


---

# ⭐ Final Note

AeroIQ transforms air quality monitoring into precision respiratory intelligence.

It does not inform after exposure — it predicts before impact.
