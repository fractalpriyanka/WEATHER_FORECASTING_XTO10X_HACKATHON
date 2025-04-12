import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from datetime import datetime
import os

class XGBRegressor:
    def __init__(self, data_path, output_dir="model"):
        self.data = pd.read_csv(data_path)
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.output_dir = output_dir
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
        os.makedirs(self.output_dir, exist_ok=True)

    def prepare_multi_day_targets(self):
        df = self.data.copy()
        for i in range(1, 8):
            df[f'temperature_t+{i}'] = df['temperature'].shift(-i)
            df[f'precipitation_t+{i}'] = df['precipitation'].shift(-i)
        return df.dropna()

    def train_test(self):
        df_multi = self.prepare_multi_day_targets()
        train_end_date = df_multi['date'].max() - pd.Timedelta(days=30)
        train = df_multi[df_multi['date'] <= train_end_date]
        test = df_multi[df_multi['date'] > train_end_date]
        X_train = train[self.features]
        X_test = test[self.features]
        y_train = train[[f'temperature_t+{i}' for i in range(1, 8)] + [f'precipitation_t+{i}' for i in range(1, 8)]]
        y_test = test[[f'temperature_t+{i}' for i in range(1, 8)] + [f'precipitation_t+{i}' for i in range(1, 8)]]
        return X_train, X_test, y_train, y_test

    def train_model(self, X_train, y_train):
        model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            random_state=42
        )
        model.fit(X_train, y_train)
        return model

    def evaluate_metrics(self, model, X_test, y_test):
        y_pred = model.predict(X_test)
        metrics = {}
        for i in range(1, 8):
            temp_r2 = r2_score(y_test[f'temperature_t+{i}'], y_pred[:, i-1])
            temp_mae = mean_absolute_error(y_test[f'temperature_t+{i}'], y_pred[:, i-1])
            precip_r2 = r2_score(y_test[f'precipitation_t+{i}'], y_pred[:, i+6])
            precip_mae = mean_absolute_error(y_test[f'precipitation_t+{i}'], y_pred[:, i+6])
            metrics[f'day_{i}'] = {
                'temperature': {'r2': temp_r2, 'mae': temp_mae},
                'precipitation': {'r2': precip_r2, 'mae': precip_mae}
            }
            print(f"Day {i}: Temp R²={temp_r2:.4f}, MAE={temp_mae:.2f}°C; Precip R²={precip_r2:.4f}, MAE={precip_mae:.2f}mm")
        return metrics

    def save_model(self, model):
        current_date = datetime.now().strftime('%Y-%m-%d')
        output_path = os.path.join(self.output_dir, f"xgb_model_{current_date}.pkl")
        joblib.dump(model, output_path)
        print(f"Model saved to {output_path}")
        return output_path

    def fit(self):
        X_train, X_test, y_train, y_test = self.train_test()
        model = self.train_model(X_train, y_train)
        metrics = self.evaluate_metrics(model, X_test, y_test)
        model_path = self.save_model(model)
        return {'model_path': model_path, 'metrics': metrics}

if __name__ == "__main__":
    regressor = XGBRegressor(data_path="data/mandi_weather_data_preprocessed.csv")
    result = regressor.fit()
    print(f"Model saved at: {result['model_path']}")