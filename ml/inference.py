import joblib
import numpy as np
import pandas as pd

artifact = joblib.load(r"D:\studies\EME\assignment\Task6\ML Model\temperature_linear_model.pkl")
model = artifact['model']
expected_features = artifact['features']

system_memory = {
    'last_valid_temp': 20.0,
    'last_valid_humidity': 50.0,
    'last_valid_rain': 0.0,
    'last_valid_wind': 5.0,
    'last_valid_cloud': 20.0,
    'temp_lag_1': 19.5, 
}

def process_raw_sensor_to_features(raw_data: dict) -> pd.DataFrame:
  if raw_data.get('sensor_status') != 'Normal':
    temp = system_memory['last_valid_temp']
    humidity = system_memory['last_valid_humidity']
    rain = system_memory['last_valid_rain']
    wind = system_memory['last_valid_wind']
    cloud = system_memory['last_valid_cloud']
  else:
    temp = raw_data['temperature_c']
    humidity = raw_data['humidity_percent']
    rain = raw_data['rainfall_mm']
    wind = raw_data['wind_speed_kmh']
    cloud = raw_data['cloud_cover_percent']

    system_memory['last_valid_temp'] = temp
    system_memory['last_valid_humidity'] = humidity
    system_memory['last_valid_rain'] = rain
    system_memory['last_valid_wind'] = wind
    system_memory['last_valid_cloud'] = cloud

  timestamp = pd.to_datetime(raw_data['timestamp'])
  h_sin = np.sin(2 * np.pi * timestamp.hour / 24.0)
  h_cos = np.cos(2 * np.pi * timestamp.hour / 24.0)
  m_sin = np.sin(2 * np.pi * timestamp.month / 12.0)
  m_cos = np.cos(2 * np.pi * timestamp.month / 12.0)

  row = {
      'temperature_c': temp,
      'humidity_percent': humidity,
      'cloud_cover_percent': cloud,
      'heatwave_flag': raw_data.get('heatwave_flag', int(temp > 40)),
      'heavy_rain_flag': raw_data.get('heavy_rain_flag', int(rain > 15)),
      'storm_flag': raw_data.get('storm_flag', int(wind > 40)),
      'rainfall_log': np.log1p(rain),
      'wind_speed_log': np.log1p(wind),
      'hour_sin': h_sin,
      'hour_cos': h_cos,
      'month_sin': m_sin,
      'month_cos': m_cos,
      'temp_lag_1': system_memory['temp_lag_1'],
  }

  current_condition = raw_data.get('weather_condition', 'Clear')
  for col in expected_features:
    if col.startswith('weather_condition_'):
      row[col] = 1 if col == f'weather_condition_{current_condition}' else 0

  feature_df = pd.DataFrame([row])


  for col in expected_features:
    if col not in feature_df.columns:
      feature_df[col] = 0

  feature_df = feature_df[expected_features]

  system_memory['temp_lag_1'] = temp

  return feature_df

# Simulating For Incoming Data
incoming_sensor_payload = {
    'timestamp': '2026-07-15 21:00:00',
    'district_id': 'D01',
    'temperature_c': 28,
    'feels_like_c': 30.0,
    'humidity_percent': 55.0,
    'rainfall_mm': 0.0,
    'wind_speed_kmh': 7.5,
    'cloud_cover_percent': 0.0,
    'weather_condition': 'Clear',
    'heatwave_flag': 0,
    'heavy_rain_flag': 0,
    'storm_flag': 0,
    'sensor_status': 'Normal',
}

X_live = process_raw_sensor_to_features(incoming_sensor_payload)

forecast_6h = model.predict(X_live)[0]

print('Next 6 Hours Tempreture:')
for hour_idx, pred_temp in enumerate(forecast_6h, start=1):
  print(f'Hour +{hour_idx}: {pred_temp:.2f} °C')