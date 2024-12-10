#!/usr/bin/env python3

import os
import json
import requests
import traceback
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Slack webhook URL
slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')

def send_slack_alert(message):
    """Send an alert message to Slack using a webhook."""
    payload = {"text": message}
    try:
        response = requests.post(slack_webhook_url, json=payload)
        response.raise_for_status()
        print("Slack notification sent.")
    except Exception as e:
        print("Failed to send Slack notification:", e)

def fetch_user_preferences():
    """Fetch user preferences from the Supabase database."""
    try:
        response = supabase.table('user_preferences').select("*").eq('deleted', False).execute()
        return response.data if response.data else []
    except Exception as e:
        print("Error fetching user preferences:", e)
        return []

def fetch_weather_data(latitude, longitude):
    """Fetch current weather data for the given location using Open-Meteo API."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        temp = data['current'].get('temperature_2m')
        humidity = data['current'].get('relative_humidity_2m')

        print(f"Weather data for ({latitude}, {longitude}): Temperature = {temp}°C, Humidity = {humidity if humidity else 'Not available'}")
        return temp, humidity
    except Exception as e:
        print(f"Failed to fetch weather data for ({latitude}, {longitude}):", e)
        return None, None

def check_preferences():
    """
    Check user preferences against current weather conditions and send alerts.
    Ensures no duplicate alerts are sent during the same run.
    """
    preferences = fetch_user_preferences()
    alerts_sent = set()  # Track sent alerts

    for pref in preferences:
        # Extract preference details
        pref_id = pref['pref_id']
        user_id = pref['user_id']
        location = pref.get('location', 'Unknown location')
        temp_min = pref['temp_min']
        temp_max = pref['temp_max']
        humidity_min = pref['humidity_min']
        humidity_max = pref['humidity_max']

        # Fetch current weather for this location's coordinates
        latitude = pref['latitude']
        longitude = pref['longitude']
        temp, humidity = fetch_weather_data(latitude, longitude)

        # Generate unique keys for temperature and humidity alerts
        temp_alert_key = f"temp-{pref_id}"
        humidity_alert_key = f"humidity-{pref_id}"

        # Check temperature range and send alert if out of bounds
        if temp is not None:
            if (temp < temp_min or temp > temp_max) and temp_alert_key not in alerts_sent:
                alert_message = (
                    f"Alert for user {user_id}, preference {pref_id}: "
                    f"Temperature {temp}°C is outside preferred range ({temp_min}°C - {temp_max}°C) "
                    f"for location '{location}'"
                )
                print(alert_message)
                send_slack_alert(alert_message)
                alerts_sent.add(temp_alert_key)  # Mark alert as sent
        else:
            print(f"Temperature data unavailable for preference {pref_id} at location '{location}'.")

        # Check humidity range and send alert if out of bounds
        if humidity is not None:
            if (humidity < humidity_min or humidity > humidity_max) and humidity_alert_key not in alerts_sent:
                alert_message = (
                    f"Alert for user {user_id}, preference {pref_id}: "
                    f"Humidity {humidity}% is outside preferred range ({humidity_min}% - {humidity_max}%) "
                    f"for location '{location}'"
                )
                print(alert_message)
                send_slack_alert(alert_message)
                alerts_sent.add(humidity_alert_key)  # Mark alert as sent
        else:
            print(f"Humidity data unavailable for preference {pref_id} at location '{location}'.")

if __name__ == "__main__":
    """Run the preference check."""
    try:
        check_preferences()
    except Exception as e:
        print("Unexpected error in main:", e)
        traceback.print_exc()
