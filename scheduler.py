from datetime import datetime
import requests
from supabase import create_client

# Initialize Supabase client (replace with your actual URL and key)
supabase = create_client("https://ewuamuzcbsrkmpjkrdmn.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV3dWFtdXpjYnNya21wamtyZG1uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAxNDE0MDIsImV4cCI6MjA0NTcxNzQwMn0.SPo5KG3ufHN0dt4Jxvl-sAJ9tZanRA9G1JxGHFrLOBc")

def check_weather_alerts():
    # Step 1: Retrieve all user preferences
    response = supabase.table("user_preferences").select("*").execute()
    preferences = response.data  # This is a list of user preference records

    for pref in preferences:
        user_id = pref["user_id"]

        # Step 2: Fetch current weather for the user's location
        weather_data = get_current_weather(pref["latitude"], pref["longitude"])
        
        # Step 3: Check if weather exceeds user-specific thresholds
        if (weather_data["temperature"] > pref["temp_max"] or 
            weather_data["temperature"] < pref["temp_min"] or 
            weather_data["humidity"] > pref["humidity_max"] or 
            weather_data["humidity"] < pref["humidity_min"]):
            
            # Step 4: Send an alert to the user
            send_alert(user_id, weather_data, pref)

def get_current_weather(latitude, longitude):
    # Make a request to your weather endpoint
    response = requests.get(f"http://127.0.0.1:5000/weather?latitude={latitude}&longitude={longitude}&start_date={datetime.now().date()}")
    return response.json()[0]  # Assuming it returns a list with one weather record

def send_alert(user_id, weather_data, pref):
    # Get user's email based on their ID from the users table
    user_info = supabase.table("users").select("email").eq("id", user_id).single().execute()
    email = user_info.data["email"]

    # Customize the alert message
    message = (f"Alert: Weather condition exceeded your set preferences.\n"
               f"Location: {pref['latitude']}, {pref['longitude']}\n"
               f"Temperature: {weather_data['temperature']}°C\n"
               f"Humidity: {weather_data['humidity']}%\n"
               f"Your Preferences:\n"
               f"- Temp Min: {pref['temp_min']}°C, Temp Max: {pref['temp_max']}°C\n"
               f"- Humidity Min: {pref['humidity_min']}%, Humidity Max: {pref['humidity_max']}%")

    # Example: send an email alert
    send_email(email, message)
    print(f"Alert sent to user {user_id} at {email}.")

def send_email(email, message):
    # Placeholder function to demonstrate email sending
    print(f"Sending email to {email} with message:\n{message}")
    # Here, you'd use an email library like SendGrid, Mailgun, or smtplib
