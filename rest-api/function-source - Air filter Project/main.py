
import io

import numpy as np
import pandas as pd
from google.cloud import storage
import pickle
# from flask import Flask, request, jsonify

storage_client = storage.Client()
bucket = storage_client.bucket("moses-daudu-bucket")
blob_model = bucket.blob("air-filter/rf_model.sav")
blob_dv = bucket.blob("air-filter/dataset/dv.pkl")
blob_model.download_to_filename("/tmp/rf_model.sav")
blob_dv.download_to_filename("/tmp/dv.pkl")

with open('/tmp/rf_model.sav', "rb") as f_in:
    model = pickle.load(f_in)

with open('/tmp/dv.pkl', "rb") as standa:
    dv = pickle.load(standa)

def prepare_features(ride):
    ride = [ride]
    df = pd.DataFrame(ride)
    df['Date'] = pd.to_datetime(df['Date'])

    df['saleyear'] = df.Date.dt.year
    df['salemonth'] = df.Date.dt.month
    df['saleday'] = df.Date.dt.day
    df['saledayofweek'] = df.Date.dt.day_of_week
    df['saledayofyear'] = df.Date.dt.day_of_year

    df= df.drop(columns=['L3_SO2_SO2_column_number_density_amf','L3_NO2_stratospheric_NO2_column_number_density','L3_CLOUD_sensor_azimuth_angle','L3_HCHO_solar_azimuth_angle','L3_SO2_sensor_zenith_angle','L3_CH4_solar_zenith_angle','temperature_2m_above_ground','L3_NO2_absorbing_aerosol_index','L3_CO_sensor_azimuth_angle','L3_AER_AI_sensor_zenith_angle','L3_AER_AI_solar_azimuth_angle','L3_AER_AI_solar_zenith_angle','L3_CO_sensor_zenith_angle','L3_HCHO_sensor_zenith_angle','L3_HCHO_tropospheric_HCHO_column_number_density_amf','L3_SO2_sensor_azimuth_angle','L3_SO2_absorbing_aerosol_index','L3_CH4_sensor_zenith_angle','specific_humidity_2m_above_ground','L3_NO2_NO2_slant_column_number_density','L3_NO2_cloud_fraction','L3_NO2_tropopause_pressure','L3_O3_sensor_azimuth_angle','L3_O3_cloud_fraction','L3_CLOUD_sensor_zenith_angle','L3_CLOUD_solar_azimuth_angle','L3_CLOUD_solar_zenith_angle','L3_CO_sensor_altitude','L3_HCHO_sensor_azimuth_angle','L3_CO_solar_zenith_angle','L3_HCHO_cloud_fraction','L3_HCHO_solar_zenith_angle','L3_HCHO_tropospheric_HCHO_column_number_density','L3_SO2_SO2_column_number_density','L3_CLOUD_cloud_top_height','L3_CLOUD_cloud_top_pressure','L3_AER_AI_absorbing_aerosol_index','L3_AER_AI_sensor_azimuth_angle','L3_SO2_SO2_slant_column_number_density','L3_SO2_cloud_fraction','L3_SO2_solar_zenith_angle','L3_CH4_aerosol_height','L3_CH4_sensor_azimuth_angle','L3_CH4_solar_azimuth_angle','Place_ID X Date','Date'], axis=1)
    
    cat = ['Place_ID','saleday', 'saledayofweek', 'saledayofyear']
    df[cat] = df[cat].astype(str)
    
    train_numerical_features=df.select_dtypes(include=['float']).columns
    train_numerical = []
    for num in train_numerical_features:
        train_numerical.append(num)

    train_categorical_features=df.select_dtypes(include=['object']).columns
    train_categorical= []
    for cat in train_categorical_features:
        train_categorical.append(cat)

    features = df[train_categorical + train_numerical].to_dict(orient='records')

    return features

def predict(features):
    x = dv.transform(features)
    preds = model.predict(x)
    return float(preds[0])


def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    # request_json = request.get_json()
    ride = request.get_json()
    
    features = prepare_features(ride)
    pred = predict(features)

    result = {
        'duration': int(pred)
    }
    return jsonify(result)
