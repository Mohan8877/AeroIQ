from flask import Flask, render_template, request
import sqlite3
import time
from src.api_fetch import get_city_coordinates, get_live_data, get_city_from_coords
from src.predict import predict_next_hour_risk 

app = Flask(__name__)

# --- ENTERPRISE SCALE: HIGH-SPEED RAM CACHING ---
# This allows 50+ concurrent users to load the page instantly without API lag
API_CACHE = {}
CACHE_TTL = 600 # Cache data for 10 minutes

def cached_get_live_data(lat, lon):
    key = f"data_{lat}_{lon}"
    now = time.time()
    if key in API_CACHE and (now - API_CACHE[key]['time']) < CACHE_TTL:
        return API_CACHE[key]['data'] # Return instant RAM data
    
    data = get_live_data(lat, lon)
    if data: API_CACHE[key] = {'time': now, 'data': data}
    return data

def cached_get_city_coordinates(city_query):
    key = f"coord_{city_query.lower()}"
    now = time.time()
    if key in API_CACHE and (now - API_CACHE[key]['time']) < CACHE_TTL:
        return API_CACHE[key]['data']
    
    lat, lon, city, country = get_city_coordinates(city_query)
    if lat: API_CACHE[key] = {'time': now, 'data': (lat, lon, city, country)}
    return lat, lon, city, country

# --- DATABASE SETUP ---
def log_patient_to_db(name, health_condition, city):
    try:
        conn = sqlite3.connect('aeroiq_database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS patient_logs 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, condition TEXT, city TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        c.execute("INSERT INTO patient_logs (name, condition, city) VALUES (?, ?, ?)", (name, health_condition, city))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")

# --- CORE LOGIC ---
def get_risk_theme(aqi):
    if aqi <= 50: return "Good", "#00ffcc", "shadow-[0_0_20px_#00ffcc]", 16
    elif aqi <= 100: return "Moderate", "#ccff00", "shadow-[0_0_20px_#ccff00]", 33
    elif aqi <= 150: return "Poor", "#ff9900", "shadow-[0_0_20px_#ff9900]", 50
    elif aqi <= 200: return "Unhealthy", "#ff0055", "shadow-[0_0_20px_#ff0055]", 66
    elif aqi <= 300: return "Severe", "#b000ff", "shadow-[0_0_20px_#b000ff]", 83
    else: return "Hazardous", "#ff0000", "shadow-[0_0_30px_#ff0000]", 95

def calculate_health_impact(aqi, predicted_risk, user_health):
    base_score = min((aqi / 300.0) * 100, 100) 
    if user_health != "Normal" and predicted_risk in ["Poor", "Unhealthy for Sensitive", "Unhealthy", "Very Unhealthy", "Severe", "Hazardous"]:
        base_score = min(base_score * 1.3, 100)
    return int(base_score)

def generate_smart_alert(predicted_risk, primary_threat, user_health, user_name):
    if predicted_risk in ["Good", "Moderate"]:
        return {"title": "Clear Skies Ahead", "msg": f"{user_name}, the upcoming hour looks perfectly safe for your health profile. Enjoy the outdoors!", "color": "#00ffcc"}
    
    if user_health == "Asthma" and primary_threat in ["PM2.5", "PM10", "NO2"]:
        msg = f"Attention {user_name}: In the next hour, {primary_threat} will surge. HIGH RISK of an asthma attack. Please stay indoors."
    elif user_health == "Heart Disease" and primary_threat in ["CO", "PM2.5"]:
        msg = f"{user_name}, 1-Hour Forecast shows rising {primary_threat}. This places extreme stress on cardiovascular systems. Avoid exertion."
    elif user_health == "COPD" and primary_threat in ["O3", "PM10", "PM2.5"]:
        msg = f"Warning {user_name}: Forecast indicates {primary_threat} levels will restrict breathing for COPD patients soon. Seal windows."
    else:
        msg = f"{user_name}, the AQI is not good. It will drop to {predicted_risk} due to {primary_threat}. We advise staying indoors."

    if predicted_risk in ["Poor", "Unhealthy for Sensitive"]:
        return {"title": "Health Caution: Air Dropping", "msg": msg, "color": "#ff9900"}
    else:
        return {"title": "🚨 CRITICAL HEALTH DANGER", "msg": msg, "color": "#ff0055"}

# --- FIXED: FULLY PERSONALIZED ACTION PLAN (Even on Good Days) ---
def generate_action_plan(predicted_risk, primary_threat, user_health):
    actions = []
    
    # 1. Condition-Specific Advice for GOOD AQI
    if predicted_risk in ["Good", "Moderate"]:
        if user_health == "Asthma":
            actions.append({"type": "Airway Clear", "color": "#00ffcc", "icon": "M5 13l4 4L19 7", "text": "Particulates are low. Excellent time for outdoor breathing exercises."})
            actions.append({"type": "Routine", "color": "#3b82f6", "icon": "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z", "text": "Maintain your standard daily maintenance inhaler schedule."})
        elif user_health == "Heart Disease":
            actions.append({"type": "Cardio Safe", "color": "#00ffcc", "icon": "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z", "text": "Optimal oxygen availability. Safe for prescribed cardiovascular exercises."})
            actions.append({"type": "Routine", "color": "#b000ff", "icon": "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z", "text": "Continue your standard blood pressure medication schedule."})
        elif user_health == "COPD":
            actions.append({"type": "Lung Safe", "color": "#00ffcc", "icon": "M5 13l4 4L19 7", "text": "Low toxic matter. Safe to thoroughly ventilate your living space."})
            actions.append({"type": "Activity", "color": "#10b981", "icon": "M14 5l7 7m0 0l-7 7m7-7H3", "text": "Good conditions for your outdoor pulmonary rehab exercises."})
        else:
            actions.append({"type": "Optimal", "color": "#00ffcc", "icon": "M5 13l4 4L19 7", "text": "Ideal time to naturally ventilate your home."})
            actions.append({"type": "Activity", "color": "#00ffcc", "icon": "M14 5l7 7m0 0l-7 7m7-7H3", "text": "Great conditions for outdoor exercise."})
        return actions

    # 2. Condition-Specific Advice for BAD AQI
    actions.append({"type": "Threat Warning", "color": "#ff9900", "icon": "M12 9v2m0 4h.01", "text": f"Prepare for elevated {primary_threat} levels in the coming hour."})

    if user_health == "Asthma":
        actions.append({"type": "Critical Protocol", "color": "#ff0055", "icon": "M19 14l-7 7m0 0l-7-7m7 7V3", "text": "Keep your rescue inhaler immediately accessible."})
        actions.append({"type": "Strict Avoidance", "color": "#ff0055", "icon": "M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636", "text": "Postpone all heavy cardio or running outdoors."})
    elif user_health == "Heart Disease":
        actions.append({"type": "Clinical Advice", "color": "#b000ff", "icon": "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6", "text": "Remain in a temperature-controlled indoor environment."})
        actions.append({"type": "Strict Avoidance", "color": "#ff0055", "icon": "M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636", "text": "Avoid engaging in heavy physical labor outside."})
    elif user_health == "COPD":
        actions.append({"type": "Clinical Advice", "color": "#b000ff", "icon": "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z", "text": "Ensure your indoor air purifier is running at maximum capacity."})
        actions.append({"type": "Strict Avoidance", "color": "#ff0055", "icon": "M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636", "text": "Never go outside without an N95 or KN95 mask."})
    else:
        actions.append({"type": "Suggestion", "color": "#ff9900", "icon": "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z", "text": "Consider reducing prolonged outdoor physical exertion."})

    return actions

def generate_comprehensive_guide(aqi, risk_text, city, user_health):
    if aqi <= 50: level = "Low"; bg = "rgba(0, 255, 204, 0.1)"; color = "#00ffcc"
    elif aqi <= 100: level = "Moderate"; bg = "rgba(204, 255, 0, 0.1)"; color = "#ccff00"
    elif aqi <= 150: level = "Elevated"; bg = "rgba(255, 153, 0, 0.1)"; color = "#ff9900"
    else: level = "High"; bg = "rgba(255, 0, 85, 0.1)"; color = "#ff0055"

    tabs = []
    if user_health == "Asthma":
        tabs = [
            {"id": "asthma_attack", "name": "Asthma Attacks", "icon": "M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z", "risk_sentence": f"Risk of an acute Asthma exacerbation is {level} when AQI in {city} is {risk_text}.", "signs": "Severe shortness of breath, chest tightness, audible wheezing, and coughing fits.", "dos": ["Keep your rescue inhaler on your person at all times.", "Run HEPA air purifiers at maximum speed indoors."], "donts": ["Do not engage in outdoor cardiovascular exercise.", "Avoid areas with strong odors, smoke, or visible dust."]},
            {"id": "airway_inflammation", "name": "Airway Inflammation", "icon": "M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01", "risk_sentence": f"Risk of bronchial tube inflammation is {level}.", "signs": "Throat irritation, chronic dry cough, burning sensation in lungs.", "dos": ["Drink warm fluids to soothe the respiratory tract.", "Wear a high-quality N95 mask if leaving the house."], "donts": ["Do not breathe cold, dry outdoor air directly.", "Do not sleep with windows open."]},
            {"id": "allergic_triggers", "name": "Allergic Triggers", "icon": "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z", "risk_sentence": f"Risk of allergen-induced asthma is {level}.", "signs": "Itchy/watery eyes, rapid sneezing, nasal congestion.", "dos": ["Wash face and hands immediately after returning indoors.", "Use saline nasal sprays."], "donts": ["Do not hang laundry outside to dry.", "Avoid dusting or sweeping without wearing a mask."]}
        ]
    elif user_health == "Heart Disease":
        tabs = [
            {"id": "cardio_stress", "name": "Cardiac Stress", "icon": "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z", "risk_sentence": f"Risk of cardiovascular strain is {level}.", "signs": "Chest discomfort, unusual fatigue, rapid heartbeat, lightheadedness.", "dos": ["Take all prescribed heart medications strictly on schedule.", "Stay in a temperature-controlled indoor environment."], "donts": ["Absolutely no heavy lifting or strenuous outdoor tasks.", "Don't ignore any chest pain."]},
            {"id": "blood_pressure", "name": "Blood Pressure", "icon": "M13 10V3L4 14h7v7l9-11h-7z", "risk_sentence": f"Risk of sudden blood pressure spikes is {level}.", "signs": "Severe headaches, pounding in chest/neck, dizziness.", "dos": ["Monitor your blood pressure using a home cuff.", "Reduce sodium intake and practice deep breathing."], "donts": ["Do not consume excess caffeine.", "Do not engage in stress-inducing activities."]},
            {"id": "hypoxia", "name": "Low Oxygen", "icon": "M20.488 9H15V3.512A9.025 9.025 0 0120.488 9zM12 2.05v7.45H4.55a9.025 9.025 0 017.45-7.45zM4.55 13h7.45v7.45a9.025 9.025 0 01-7.45-7.45zm9.45 7.45V13h7.45a9.025 9.025 0 01-7.45 7.45z", "risk_sentence": f"Risk of blood oxygen depletion is {level}.", "signs": "Confusion, restlessness, bluish tint in lips, shortness of breath at rest.", "dos": ["Use supplemental oxygen if prescribed.", "Ensure excellent indoor ventilation."], "donts": ["Do not exert yourself physically.", "Do not smoke."]}
        ]
    elif user_health == "COPD":
        tabs = [
            {"id": "copd_flare", "name": "COPD Flare-up", "icon": "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z", "risk_sentence": f"Risk of a severe COPD exacerbation is {level}.", "signs": "Increase in severe shortness of breath, more coughing than usual.", "dos": ["Follow your COPD action plan immediately.", "Use maintenance inhalers."], "donts": ["Never go outside without wearing an N95 mask.", "Do not ignore a drop in oxygen levels."]},
            {"id": "chest_tightness", "name": "Chest Tightness", "icon": "M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10", "risk_sentence": f"Risk of restricted lung capacity is {level}.", "signs": "Feeling like you cannot expand lungs fully, rapid shallow breathing.", "dos": ["Practice pursed-lip breathing.", "Sit in a relaxed, supported position."], "donts": ["Do not panic.", "Avoid lying completely flat."]},
            {"id": "mucus_buildup", "name": "Mucus Buildup", "icon": "M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z", "risk_sentence": f"Risk of excess pulmonary secretion is {level}.", "signs": "Productive cough producing thick sputum, rattling sound.", "dos": ["Stay highly hydrated.", "Perform controlled coughing techniques."], "donts": ["Do not take over-the-counter cough suppressants.", "Avoid dairy."]}
        ]
    else: 
        tabs = [
            {"id": "headaches", "name": "Headaches", "icon": "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z", "risk_sentence": f"Risk of Headaches symptoms is {level}.", "signs": "Pressure around forehead/temples, fatigue, difficulty concentrating.", "dos": ["Choose indoor, clean air.", "Stay hydrated and take breaks from devices."], "donts": ["Try not to do intense outdoor exercise.", "Don't ignore unusual symptoms."]},
            {"id": "allergies", "name": "Allergies", "icon": "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z", "risk_sentence": f"Risk of Allergic Rhinitis is {level}.", "signs": "Itchy/watery eyes, constant sneezing, congested nose.", "dos": ["Wash face/hands after returning indoors.", "Use saline nasal sprays."], "donts": ["Do not sleep with windows open.", "Avoid hanging laundry outside."]},
            {"id": "fatigue", "name": "Fatigue", "icon": "M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z", "risk_sentence": f"Risk of general lethargy is {level}.", "signs": "Feeling unusually tired, lack of energy, brain fog.", "dos": ["Ensure sleeping environment is purified.", "Take frequent breaks during tasks."], "donts": ["Avoid pushing through exhaustion.", "Do not rely heavily on caffeine."]}
        ]

    return {"theme": {"bg": bg, "color": color, "level": level}, "tabs": tabs}

@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "GET": return render_template("index.html", show_onboarding=True)

    user_name = request.form.get("user_name", "Guest")
    user_health = request.form.get("user_health")
    if not user_health or user_health == "": user_health = "Normal"
    
    lat, lon, official_city, country = None, None, None, None

    # Exact GPS coordinates passed by the Profile Switcher
    if "gps_lat" in request.form and request.form["gps_lat"] and request.form["gps_lat"] != "None":
        try:
            lat, lon = float(request.form["gps_lat"]), float(request.form["gps_lon"])
            # Use cached reverse geocoding
            official_city, country = get_city_from_coords(lat, lon)
        except ValueError: pass

    # If new search
    if not lat:
        city_query = request.form.get("city_name")
        if not city_query or city_query.strip() == "": city_query = request.form.get("current_city", "Delhi")
        # Use cached coordinates
        lat, lon, official_city, country = cached_get_city_coordinates(city_query)

    if not lat: 
        return render_template("index.html", show_onboarding=True, error_message=f"Location '{city_query}' is invalid. Please verify spelling.")

    # Use High-Speed Cached Live Data
    live_data = cached_get_live_data(lat, lon)
    if not live_data: 
        return render_template("index.html", show_onboarding=True, error_message="Live AQI data is currently unavailable for this region.")

    log_patient_to_db(user_name, user_health, official_city)

    pollutants = live_data.get("Pollutants", {})
    predicted_risk = predict_next_hour_risk(live_data.get("ML_Pollutants", {}))
    aqi = live_data.get("Live_AQI", 0)
    risk_text, risk_color, risk_glow, slider_pos = get_risk_theme(aqi)
    
    primary_threat = max(pollutants, key=pollutants.get).split()[0] if pollutants else "None"
    
    smart_alert = generate_smart_alert(predicted_risk, primary_threat, user_health, user_name)
    action_plan = generate_action_plan(predicted_risk, primary_threat, user_health) 
    health_impact_score = calculate_health_impact(aqi, predicted_risk, user_health)
    health_guide = generate_comprehensive_guide(aqi, risk_text, official_city, user_health)

    return render_template(
        "index.html",
        show_onboarding=False, user_name=user_name, user_health=user_health,
        city=official_city, country=country,
        current_lat=lat, current_lon=lon,
        aqi=aqi, risk_text=risk_text, risk_color=risk_color, risk_glow=risk_glow, slider_pos=slider_pos,
        pollutants=pollutants, weather=live_data.get("Weather", {}),
        predicted_risk=predicted_risk, smart_alert=smart_alert, 
        action_plan=action_plan, primary_threat=primary_threat,
        forecast=live_data.get("Forecast", {}), health_impact_score=health_impact_score,
        health_guide=health_guide
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
