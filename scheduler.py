import json
import requests
import time
import traceback
from apscheduler.schedulers.blocking import BlockingScheduler
from supabase import create_client, Client
import os

# Supabase credentials
supabase_url = 'https://ewuamuzcbsrkmpjkrdmn.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV3dWFtdXpjYnNya21wamtyZG1uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAxNDE0MDIsImV4cCI6MjA0NTcxNzQwMn0.SPo5KG3ufHN0dt4Jxvl-sAJ9tZanRA9G1JxGHFrLOBc'
supabase: Client = create_client(supabase_url, supabase_key)

# Slack webhook URL (replace with your actual Slack Webhook URL)
slack_webhook_url = "https://hooks.slack.com/services/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"

def send_slack_alert(message):
    """Send an alert message to Slack using a webhook."""
    payload = {"text": message}
    try:
        response = requests.post(slack_webhook_url, json=payload)
        response.raise_for_status()  # Check if request was successful
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
        response.raise_for_status()  # Raises an HTTPError if the response status is 4xx or 5xx
        data = response.json()

        # Save the response data to a JSON file for inspection
        #with open("weather_response.json", "w") as file:
            #json.dump(data, file, indent=4)
        
        # Parse the temperature and humidity from the 'current' key
        temp = data['current'].get('temperature_2m')
        humidity = data['current'].get('relative_humidity_2m')
        
        # Print out the retrieved weather data
        print(f"Weather data for location ({latitude}, {longitude}): Temperature = {temp}°C, Humidity = {humidity if humidity is not None else 'Not available'}")
        
        return temp, humidity
    except Exception as e:
        print(f"Failed to fetch weather data for ({latitude}, {longitude}):", e)
        return None, None

def check_preferences():
    """Check each user's preferences and alert if conditions are outside range."""
    preferences = fetch_user_preferences()
    
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
        
        # Check and alert based on temperature and humidity preferences
        if temp is not None:
            if temp < temp_min or temp > temp_max:
                alert_message = (
                    f"Alert for user {user_id}, preference {pref_id}: "
                    f"Temperature {temp}°C is outside preferred range ({temp_min}°C - {temp_max}°C) "
                    f"for location '{location}'"
                )
                print(alert_message)
                send_slack_alert(alert_message)
        else:
            print(f"Failed to retrieve temperature data for preference {pref_id} at location '{location}'.")

        time.sleep(15)

        # Handle humidity if available
        if humidity is not None:
            if humidity < humidity_min or humidity > humidity_max:
                alert_message = (
                    f"Alert for user {user_id}, preference {pref_id}: "
                    f"Humidity {humidity}% is outside preferred range ({humidity_min}% - {humidity_max}%) "
                    f"for location '{location}'"
                )
                print(alert_message)
                send_slack_alert(alert_message)
        else:
            print(f"Humidity data not available for preference {pref_id} at location '{location}'.")
        time.sleep(15)

def schedule_checks():
    """Schedule the preference checks to run every hour, with an immediate initial run."""
    scheduler = BlockingScheduler()
    
    # Schedule the job to run every hour
    scheduler.add_job(check_preferences, 'interval', hours=1)

    # Run the check_preferences function once immediately
    try:
        print("Running initial check...")
        check_preferences()  # Run once on launch
    except Exception as e:
        print("Error during initial check:", e)
        traceback.print_exc()

    # Start the scheduler
    try:
        print("Starting scheduler...")
        scheduler.start()
    except Exception as e:
        print("Error starting scheduler:", e)
        traceback.print_exc()

if __name__ == "__main__":
    try:
        schedule_checks()
    except Exception as e:
        print("Unexpected error in main:", e)
        traceback.print_exc()
        time.sleep(10)  # Delay to allow you to see the error before the window closes
