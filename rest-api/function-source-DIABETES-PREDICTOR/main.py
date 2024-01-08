from flask import Flask,request, jsonify
import numpy as np
import pandas as pd
import pickle
from google.cloud import storage


storage_client = storage.Client()
bucket = storage_client.get_bucket('moses-daudu-bucket')
blob_classifier = bucket.blob('models/diabetes_svm_model.pkl')
blob_scaler = bucket.blob('models/scaler_min_max.pkl')
blob_classifier.download_to_filename('/tmp/diabetes_svm_model.pkl')
blob_scaler.download_to_filename('/tmp/scaler_min_max.pkl')

model = pickle.load(open('/tmp/diabetes_svm_model.pkl', 'rb'))
processor = pickle.load(open('/tmp/scaler_min_max.pkl', 'rb'))

def hello_world(request):
  """Responds to any HTTP request.
  Args:
      request (flask.Request): HTTP request object.
  Returns:
      The response text or any set of values that can be turned into a
      Response object using
      `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
  """
  request_json = request.get_json()

  Pregnancies = request_json['Pregnancies']
  Glucose = request_json['Glucose']
  BloodPressure = request_json['BloodPressure']
  SkinThickness = request_json['SkinThickness']
  Insulin = request_json['Insulin']
  BMI = request_json['BMI']
  DiabetesPedigreeFunction = request_json['DiabetesPedigreeFunction']
  Age = request_json['Age']
  row_values = [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]

  x_new = np.array(row_values).reshape(1, -1)
  x_new_scaler = processor.transform(x_new)
  y_new_pred = model.predict(x_new_scaler)

  result = {
    "prediction": int(y_new_pred[0])
  }

  return jsonify(result)
