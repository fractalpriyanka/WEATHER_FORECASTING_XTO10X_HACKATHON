import pandas as pd
import numpy as np
import os

class PreProcessData:
    @staticmethod
    def add_features(df):
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['temp_range'] = df['temp_max'] - df['temp_min']
        df['humidity_cloud'] = df['humidity'] * df['cloud_cover'] / 100
        df['wind_x'] = df['wind_speed'] * np.cos(np.radians(df['wind_direction']))
        df['wind_y'] = df['wind_speed'] * np.sin(np.radians(df['wind_direction']))
        df['dewpoint_diff'] = df['temperature'] - df['dew_point']
        df['pressure_change'] = df['surface_pressure'] - df['surface_pressure'].shift(1)
        df['day'] = df['date'].dt.day
        df['month'] = df['date'].dt.month

        for lag in [1, 2, 3]:
            for col in ['temperature', 'precipitation', 'humidity', 'wind_speed', 'wind_direction',
                        'cloud_cover', 'surface_pressure', 'dew_point', 'temp_max', 'temp_min',
                        'temp_range', 'humidity_cloud', 'wind_x', 'wind_y', 'dewpoint_diff',
                        'pressure_change']:
                df[f'{col}_lag_{lag}'] = df[col].shift(lag)

        historical_avg = df.groupby(['month', 'day']).agg({
            'temperature': 'mean',
            'precipitation': 'mean',
            'humidity': 'mean',
            'wind_speed': 'mean',
            'wind_direction': 'mean',
            'cloud_cover': 'mean',
            'surface_pressure': 'mean',
            'dew_point': 'mean',
            'temp_max': 'mean',
            'temp_min': 'mean'
        }).reset_index()
        historical_avg.columns = ['month', 'day'] + [f'historical_avg_{col}' for col in historical_avg.columns[2:]]
        df = df.merge(historical_avg, on=['month', 'day'], how='left')

        return df.dropna()

if __name__ == "__main__":
    city = "Mandi"
    input_file = f"data/{city.lower()}_weather_data.csv"
    output_file = f"data/{city.lower()}_weather_data_preprocessed.csv"
    
    if os.path.exists(input_file):
        df = pd.read_csv(input_file, parse_dates=['date'])
        df_processed = PreProcessData.add_features(df)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df_processed.to_csv(output_file, index=False)
        print(f"Preprocessed data saved to {output_file}")
    else:
        print(f"Input file {input_file} does not exist.")