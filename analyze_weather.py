import pandas as pd
import matplotlib.pyplot as plt
from supabase import create_client, Client
import os

# Supabase configuration
supabase_url = "https://ewuamuzcbsrkmpjkrdmn.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV3dWFtdXpjYnNya21wamtyZG1uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAxNDE0MDIsImV4cCI6MjA0NTcxNzQwMn0.SPo5KG3ufHN0dt4Jxvl-sAJ9tZanRA9G1JxGHFrLOBc"  # Replace with your actual key
supabase: Client = create_client(supabase_url, supabase_key)

def fetch_weather_data():
    """
    Fetches weather data from Supabase and saves it as a CSV file.
    """
    response = supabase.from_("weather_data").select("*").execute()

    if response.error:
        print("Error fetching data:", response.error)
        return None
    
    # Convert the data to a pandas DataFrame and save as CSV
    df = pd.DataFrame(response.data)
    df.to_csv('weather_data.csv', index=False)
    return df

def analyze_weather_data():
    """
    Reads weather data from a CSV file and generates plots for temperature and humidity over time.
    """
    # Fetch and save data as CSV
    df = fetch_weather_data()
    if df is None:
        return  # Exit if data could not be fetched

    # Ensure 'datetime' column is in datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Temperature Plot
    plt.figure(figsize=(10, 5))
    plt.plot(df['datetime'], df['temperature'], marker='o')
    plt.title('Temperature Over Time')
    plt.xlabel('Datetime')
    plt.ylabel('Temperature (°C)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('temperature_over_time.png')
    plt.show()

    # Humidity Plot
    plt.figure(figsize=(10, 5))
    plt.plot(df['datetime'], df['humidity'], marker='o', color='orange')
    plt.title('Humidity Over Time')
    plt.xlabel('Datetime')
    plt.ylabel('Humidity (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('humidity_over_time.png')
    plt.show()

if __name__ == "__main__":
    analyze_weather_data()
