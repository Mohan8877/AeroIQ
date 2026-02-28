import requests
from datetime import datetime

def get_city_coordinates(city_name):
    """Translates a city name into Latitude and Longitude."""
    url = f"https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                loc = data["results"][0]
                return loc["latitude"], loc["longitude"], loc["name"], loc.get("country", "")
    except Exception: pass
    return None, None, None, None

def get_city_from_coords(lat, lon):
    """Reverse geocoding: Translates Live GPS coordinates into a City Name."""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10}
    headers = {'User-Agent': 'AeroPredict-App/1.0'}
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            city = address.get("city") or address.get("town") or address.get("county", "Unknown Location")
            return city, address.get("country", "")
    except Exception: pass
    return "Your Location", "Live"

def get_live_data(lat, lon):
    """Fetches real-time AQI, Weather, and 12-Hour Forecast Data."""
    aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    weather_url = "https://api.open-meteo.com/v1/forecast"
    
    # Requesting hourly forecast for the graph
    aqi_params = {
        "latitude": lat, "longitude": lon,
        "current": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi",
        "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi",
        "forecast_days": 2
    }
    
    weather_params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"
    }

    result = {"Forecast": {}}
    
    try:
        aqi_res = requests.get(aqi_url, params=aqi_params)
        if aqi_res.status_code == 200:
            data = aqi_res.json()
            current = data.get("current", {})
            
            result["Live_AQI"] = current.get("us_aqi", 0)
            result["Pollutants"] = {
                "PM2.5": current.get("pm2_5", 0),
                "PM10": current.get("pm10", 0),
                "CO": current.get("carbon_monoxide", 0),
                "NO2": current.get("nitrogen_dioxide", 0),
                "SO2": current.get("sulphur_dioxide", 0),
                "O3": current.get("ozone", 0)
            }
            # Feature matching for your ML Model
            result["ML_Pollutants"] = {
                "PM10 (µg/m³)": current.get("pm10", 0), "PM2.5 (µg/m³)": current.get("pm2_5", 0),
                "CO (µg/m³)": current.get("carbon_monoxide", 0), "NO2 (µg/m³)": current.get("nitrogen_dioxide", 0),
                "SO2 (µg/m³)": current.get("sulphur_dioxide", 0), "O3 (µg/m³)": current.get("ozone", 0)
            }
            
            # Extract EXACTLY 12 Hours starting from the CURRENT hour
            hourly = data.get("hourly", {})
            times = hourly.get("time", [])
            current_time_str = current.get("time")
            
            if current_time_str in times:
                idx = times.index(current_time_str)
                slice_end = min(idx + 12, len(times)) 
                
                # Format time for the Chart.js graph (e.g., "02:00 PM")
                formatted_times = [datetime.strptime(t, "%Y-%m-%dT%H:%M").strftime("%I:%M %p") for t in times[idx:slice_end]]
                
                result["Forecast"] = {
                    "times": formatted_times,
                    "AQI": hourly.get("us_aqi", [])[idx:slice_end],
                    "PM2.5": hourly.get("pm2_5", [])[idx:slice_end],
                    "PM10": hourly.get("pm10", [])[idx:slice_end],
                    "CO": hourly.get("carbon_monoxide", [])[idx:slice_end],
                    "NO2": hourly.get("nitrogen_dioxide", [])[idx:slice_end],
                    "SO2": hourly.get("sulphur_dioxide", [])[idx:slice_end],
                    "O3": hourly.get("ozone", [])[idx:slice_end]
                }
    except Exception as e:
        print(f"Error fetching AQI: {e}")

    try:
        weather_res = requests.get(weather_url, params=weather_params)
        if weather_res.status_code == 200:
            data = weather_res.json().get("current", {})
            result["Weather"] = {"Temp": data.get("temperature_2m", "--"), "Humidity": data.get("relative_humidity_2m", "--"), "Wind": data.get("wind_speed_10m", "--")}
    except Exception:
        result["Weather"] = {"Temp": "--", "Humidity": "--", "Wind": "--"}

    return result