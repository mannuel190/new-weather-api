#!/usr/bin/env python3


from flask import Flask, jsonify, request, render_template  # Import render_template
from supabase import create_client, Client
from flask_cors import CORS
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Supabase configuration
SUPABASE_URL = 'https://ewuamuzcbsrkmpjkrdmn.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV3dWFtdXpjYnNya21wamtyZG1uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAxNDE0MDIsImV4cCI6MjA0NTcxNzQwMn0.SPo5KG3ufHN0dt4Jxvl-sAJ9tZanRA9G1JxGHFrLOBc'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def login_page():
    return render_template('login.html')

@app.route("/register")
def registration_page():
    return render_template('user_registration.html')

@app.route("/fetch_weather")
def weather_page():
    return render_template('fetch_weather.html') 

@app.route("/preferences")
def preferences_page():
    return render_template('user_preferences.html')  

def fetch_weather_data(latitude, longitude, start_date, end_date):
    URL = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m,relative_humidity_2m"
    
    response = requests.get(URL)
    response.raise_for_status()
    data = response.json()

    # Extract hourly data
    temperature_data = data['hourly']['temperature_2m']
    humidity_data = data['hourly']['relative_humidity_2m']
    time_series = data['hourly']['time']

    weather_list = [
        {
            'datetime': time,
            'temperature': temp,
            'humidity': humidity
        }
        for time, temp, humidity in zip(time_series, temperature_data, humidity_data)
    ]

    # Insert each record into the Supabase table
    for record in weather_list:
        supabase.table("weather_data").insert(record).execute()

    return weather_list

@app.route('/weather', methods=['GET'])
def weather_endpoint():
    try:
        # Get query parameters with default values
        latitude = request.args.get('latitude', '53.03')
        longitude = request.args.get('longitude', '7.3')
        start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'))

        weather_data = fetch_weather_data(latitude, longitude, start_date, end_date)
        return jsonify(weather_data)
    except requests.HTTPError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)  # Run the app on port 5001
