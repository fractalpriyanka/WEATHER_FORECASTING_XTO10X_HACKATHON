from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import os
from github_storage import GitHubStorage
from preprocess import PreProcessData

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://weather-app.bhaweshagrawal.com.np", "192.168.101.2:3000", "https://weather-app-five-beige-86.vercel.app"],  # Add your Vercel URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Allow POST and OPTIONS for /predict
    allow_headers=["Content-Type"],
)

GITHUB_REPO = "Bhawesh-Agrawal/weather-app"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")
MODEL_PATH = "model/xgb_model_latest.pkl"
DATASET_PATH = "data/mandi_weather_data_preprocessed.csv"

class ModelService:
    def __init__(self):
        self.model = None
        self.data = None
        self.features = [
            'temperature', 'precipitation', 'humidity', 'wind_speed', 'wind_direction',
            'cloud_cover', 'surface_pressure', 'dew_point', 'temp_max', 'temp_min',
            'temp_range', 'humidity_cloud', 'wind_x', 'wind_y', 'dewpoint_diff',
            'pressure_change', 'day', 'month',
            'temperature_lag_1', 'precipitation_lag_1', 'humidity_lag_1', 'wind_speed_lag_1',
            'wind_direction_lag_1', 'cloud_cover_lag_1', 'surface_pressure_lag_1',
            'dew_point_lag_1', 'temp_max_lag_1', 'temp_min_lag_1', 'temp_range_lag_1',
            'humidity_cloud_lag_1', 'wind_x_lag_1', 'wind_y_lag_1', 'dewpoint_diff_lag_1',
            'pressure_change_lag_1',
            'temperature_lag_2', 'precipitation_lag_2', 'humidity_lag_2', 'wind_speed_lag_2',
            'wind_direction_lag_2', 'cloud_cover_lag_2', 'surface_pressure_lag_2',
            'dew_point_lag_2', 'temp_max_lag_2', 'temp_min_lag_2', 'temp_range_lag_2',
            'humidity_cloud_lag_2', 'wind_x_lag_2', 'wind_y_lag_2', 'dewpoint_diff_lag_2',
            'pressure_change_lag_2',
            'temperature_lag_3', 'precipitation_lag_3', 'humidity_lag_3', 'wind_speed_lag_3',
            'wind_direction_lag_3', 'cloud_cover_lag_3', 'surface_pressure_lag_3',
            'dew_point_lag_3', 'temp_max_lag_3', 'temp_min_lag_3', 'temp_range_lag_3',
            'humidity_cloud_lag_3', 'wind_x_lag_3', 'wind_y_lag_3', 'dewpoint_diff_lag_3',
            'pressure_change_lag_3',
            'historical_avg_temperature', 'historical_avg_precipitation',
            'historical_avg_humidity', 'historical_avg_wind_speed',
            'historical_avg_wind_direction', 'historical_avg_cloud_cover',
            'historical_avg_surface_pressure', 'historical_avg_dew_point',
            'historical_avg_temp_max', 'historical_avg_temp_min'
        ]

    def load_from_github(self):
        storage = GitHubStorage(GITHUB_REPO, GITHUB_TOKEN)
        storage.download_file("dataset", DATASET_PATH)
        storage.download_file("model", MODEL_PATH)
        self.data = pd.read_csv(DATASET_PATH, parse_dates=['date'])
        self.model = joblib.load(MODEL_PATH)

model_service = ModelService()

@app.on_event("startup")
async def startup_event():
    try:
        model_service.load_from_github()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model/data: {e}")

class PredictionInput(BaseModel):
    date: str

@app.get("/health")
async def health_check():
    return {"status": "API is running"}

@app.post("/predict")
async def predict(input: PredictionInput):
    try:
        forecast_date = pd.to_datetime(input.date)
        latest_data = model_service.data[model_service.data['date'] == model_service.data['date'].max()]
        if latest_data.empty:
            raise HTTPException(status_code=404, detail="No recent data")
        X_pred = latest_data[model_service.features]
        predictions = model_service.model.predict(X_pred)[0]
        results = {}
        for i in range(7):
            pred_date = (forecast_date + pd.Timedelta(days=i)).strftime('%Y-%m-%d')
            # Get humidity from data or predictions (assuming humidity is in features)
            humidity_idx = model_service.features.index('humidity') if 'humidity' in model_service.features else None
            humidity = float(latest_data['humidity'].iloc[0]) if humidity_idx is None else float(predictions[humidity_idx])
            # Determine weather condition
            precipitation = float(predictions[i + 7])
            cloud_cover_idx = model_service.features.index('cloud_cover') if 'cloud_cover' in model_service.features else None
            cloud_cover = float(latest_data['cloud_cover'].iloc[0]) if cloud_cover_idx is None else float(predictions[cloud_cover_idx])
            if precipitation > 0.1:  # Threshold for rain (mm/hour)
                condition = "raining"
            elif cloud_cover > 50:  # Threshold for cloudy (%)
                condition = "cloudy"
            else:
                condition = "sunny"
            results[pred_date] = {
                'temperature': float(predictions[i]),
                'precipitation': precipitation,
                'humidity': humidity,
                'condition': condition
            }
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")