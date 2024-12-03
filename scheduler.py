#!/usr/bin/env python3

import json
import requests
import time
import traceback
from apscheduler.schedulers.blocking import BlockingScheduler
from supabase import create_client, Client
import os

# Supabase configuration
supabase_url = 'https://ewuamuzcbsrkmpjkrdmn.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV3dWFtdXpjYnNya21wamtyZG1uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAxNDE0MDIsImV4cCI6MjA0NTcxNzQwMn0.SPo5KG3ufHN0dt4Jxvl-sAJ9tZanRA9G1JxGHFrLOBc'
supabase: Client = create_client(supabase_url, supabase_key)

# Slack webhook URL (replace with your actual Slack Webhook URL)
slack_webhook_url = "https://hooks.slack.com/services/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"

def send_slack_alert(message):
    """
    Sends an alert message to Slack using a webhook.
    Used to notify users of weather conditions outside preferences.
    """
    payload = {"text": message}
    try:
        response = requests.post(slack_webhook_url, json=payload)
        response.raise_for_status()  # Raise exception if request fails
        print("Slack notification sent.")
    except Exception as e:
        print("Failed to send Slack notification:", e)

def fetch_user_preferences():
    """
    Fetch user preferences from the Supabase database.
    Returns preferences marked as not deleted.
    """
    try:
        response = supabase.table('user_preferences').select("*").eq('deleted', False).execute()
        return response.data if response.data else []
    except Exception as e:
        print("Error fetching user preferences:", e)
        return []

def fetch_weather_data(latitude, longitude):
    """
    Fetch current weather data from Open-Meteo API for the given coordinates.
    Parses temperature and humidity from the response.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception if API call fails
        data = response.json()
        
        # Extract temperature and humidity
        temp = data['current'].get('temperature_2m')
        humidity = data['current'].get('relative_humidity_2m')

        print(f"Weather data for ({latitude}, {longitude}): Temperature = {temp}°C, Humidity = {humidity if humidity else 'Not available'}")
        return temp, humidity
    except Exception as e:
        print(f"Failed to fetch weather data for ({latitude}, {longitude}):", e)
        return None, None

def check_preferences():
    """
    Check user preferences against current weather conditions.
    Sends Slack alerts for any out-of-range conditions.
    """
    preferences = fetch_user_preferences()
    
    for pref in preferences:
        # Extract user preference details
        pref_id = pref['pref_id']
        user_id = pref['user_id']
        location = pref.get('location', 'Unknown location')
        temp_min = pref['temp_min']
        temp_max = pref['temp_max']
        humidity_min = pref['humidity_min']
        humidity_max = pref['humidity_max']

        # Fetch weather data for the given coordinates
        latitude = pref['latitude']
        longitude = pref['longitude']
        temp, humidity = fetch_weather_data(latitude, longitude)

        # Check temperature range and alert if out of bounds
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
            print(f"Temperature data unavailable for preference {pref_id} at location '{location}'.")

        time.sleep(15)  # Delay to prevent rate-limiting issues

        # Check humidity range and alert if out of bounds
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
            print(f"Humidity data unavailable for preference {pref_id} at location '{location}'.")
        time.sleep(15)  # Delay to prevent rate-limiting issues

def schedule_checks():
    """
    Schedule regular checks for user preferences every hour.
    Runs an immediate check on startup for initial feedback.
    """
    scheduler = BlockingScheduler()
    
    # Schedule the job to check preferences every hour
    scheduler.add_job(check_preferences, 'interval', hours=1)

    # Run an initial check immediately
    try:
        print("Running initial check...")
        check_preferences()
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
    """
    Entry point for the script.
    Initializes and starts the preference check scheduler.
    """
    try:
        schedule_checks()
    except Exception as e:
        print("Unexpected error in main:", e)
        traceback.print_exc()
        time.sleep(10)  # Delay to allow the error to be visible before exit
