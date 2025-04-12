import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time

def fetch_open_meteo_data(lat, lon, start_date, end_date):
    url = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
           f"&start_date={start_date}&end_date={end_date}"
           "&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,"
           "relative_humidity_2m_mean,wind_speed_10m_max,wind_direction_10m_dominant,"
           "cloud_cover_mean,surface_pressure_mean,dew_point_2m_mean&timezone=auto")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Open-Meteo request failed: {response.status_code}")

def parse_open_meteo_to_df(json_data):
    daily = json_data['daily']
    return pd.DataFrame({
        'date': pd.to_datetime(daily['time']),
        'temp_max': daily['temperature_2m_max'],
        'temp_min': daily['temperature_2m_min'],
        'temperature': daily['temperature_2m_mean'],
        'precipitation': daily['precipitation_sum'],
        'humidity': daily['relative_humidity_2m_mean'],
        'wind_speed': daily['wind_speed_10m_max'],
        'wind_direction': daily['wind_direction_10m_dominant'],
        'cloud_cover': daily['cloud_cover_mean'],
        'surface_pressure': daily['surface_pressure_mean'],
        'dew_point': daily['dew_point_2m_mean']
    })

def get_city_coordinates(city):
    url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
    headers = {"User-Agent": "WeatherApp/1.0"}
    response = requests.get(url, headers=headers)
    time.sleep(1)
    if response.status_code == 200:
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        raise ValueError(f"No coordinates found for {city}")
    raise Exception(f"Nominatim request failed: {response.status_code}")

def fetch_weatherapi_data(city, api_key, date):
    url = f"http://api.weatherapi.com/v1/history.json?key={api_key}&q={city}&dt={date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"WeatherAPI request failed: {response.status_code}")

def parse_weatherapi_to_df(json_data, historical_df):
    day_data = json_data['forecast']['forecastday'][0]['day']
    date = json_data['forecast']['forecastday'][0]['date']
    condition = day_data['condition']['text'].lower()
    cloud_cover = 0 if 'sunny' in condition else 50 if 'cloudy' in condition else 100 if 'overcast' in condition else 30
    temp = day_data['avgtemp_c']
    rh = day_data['avghumidity']
    dew_point = temp - ((100 - rh) / 5)
    return pd.DataFrame({
        'date': [pd.to_datetime(date)],
        'temp_max': [day_data['maxtemp_c']],
        'temp_min': [day_data['mintemp_c']],
        'temperature': [day_data['avgtemp_c']],
        'precipitation': [day_data['totalprecip_mm']],
        'humidity': [day_data['avghumidity']],
        'wind_speed': [day_data['maxwind_kph'] / 3.6],
        'wind_direction': [historical_df['wind_direction'].mode()[0] if not historical_df.empty else 0],
        'cloud_cover': [cloud_cover],
        'surface_pressure': [historical_df['surface_pressure'].mean() if not historical_df.empty else 1013],
        'dew_point': [dew_point]
    })

def update_dataset(city, api_key, output_file, start_date="1947-01-01"):
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    if os.path.exists(output_file):
        df = pd.read_csv(output_file, parse_dates=['date'])
        last_date = df['date'].max().strftime('%Y-%m-%d')
        if last_date >= today:
            print(f"Dataset up-to-date until {today}")
            return df
    else:
        df = pd.DataFrame()

    if df.empty or df['date'].max() < pd.to_datetime(yesterday):
        lat, lon = get_city_coordinates(city)
        json_data = fetch_open_meteo_data(lat, lon, start_date, yesterday)
        new_data = parse_open_meteo_to_df(json_data)
        df = pd.concat([df, new_data], ignore_index=True)
        print(f"Fetched Open-Meteo data from {start_date} to {yesterday}")

    try:
        json_data = fetch_weatherapi_data(city, api_key, today)
        today_data = parse_weatherapi_to_df(json_data, df)
        df = pd.concat([df, today_data], ignore_index=True)
        print(f"Added WeatherAPI data for {today}")
    except Exception as e:
        print(f"Error fetching WeatherAPI data: {e}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Dataset saved to {output_file}")
    return df

if __name__ == "__main__":
    city = "Mandi"
    api_key = "e0b14f8d0606419bafe94608251104"
    output_file = "data/mandi_weather_data.csv"
    update_dataset(city, api_key, output_file)