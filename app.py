#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template  # Import render_template
from supabase import create_client, Client
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
from config import OPEN_CAGE_API_KEY, OPEN_CAGE_URL
from config import MAPBOX_ACCESS_TOKEN
from config import SUPABASE_URL, SUPABASE_KEY


# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def login():
    return render_template(
        'login.html',
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY
    )

@app.route("/register")
def registration_page():
    return render_template(
        'user_registration.html',
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY
    )

@app.route('/fetch_weather')
def fetch_weather():
    return render_template(
        'fetch_weather.html',
        mapbox_access_token=MAPBOX_ACCESS_TOKEN
    )

@app.route('/preferences')
def user_preferences():
    return render_template(
        'user_preferences.html',
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY
    )

@app.route('/geocode')
def geocode():
    location = request.args.get('location')
    if not location:
        return jsonify({"error": "Location is required"}), 400
    
    # Building OpenCage API URL
    url = f"{OPEN_CAGE_URL}?q={location}&key={OPEN_CAGE_API_KEY}"
    try:
        # Makeing call
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

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
    app.run(debug=True, port=5001)  # Run the app on port 5001
