from fetch_data import update_dataset
from preprocess import PreProcessData
from model import XGBRegressor

def daily_update():
    city = "Mandi"
    api_key = "e0b14f8d0606419bafe94608251104"
    
    # Update dataset
    raw_file = "data/mandi_weather_data.csv"
    df = update_dataset(city, api_key, raw_file)
    
    # Preprocess
    preprocessed_file = "data/mandi_weather_data_preprocessed.csv"
    df_processed = PreProcessData.add_features(df)
    df_processed.to_csv(preprocessed_file, index=False)
    print(f"Preprocessed data saved to {preprocessed_file}")
    
    # Retrain model
    regressor = XGBRegressor(data_path=preprocessed_file)
    result = regressor.fit()
    model_file = result['model_path']
    
    # Upload handled by GitHub Actions
    print(f"Ready to upload {preprocessed_file} and {model_file}")

if __name__ == "__main__":
    daily_update()