import io
import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image
from google.cloud import storage

from flask import Flask, request, jsonify

storage_client = storage.Client()
bucket = storage_client.bucket("moses-daudu-bucket")
blob_classifier = bucket.blob("models/nn.h5")
blob_classifier.download_to_filename("/tmp/nn.h5")

model = keras.models.load_model("/tmp/nn.h5")

def transform_image(pillow_image):
  data = np.asarray(pillow_image)
  data = data / 255.0
  data = data[np.newaxis, ..., np.newaxis]
  # --> [1, x, y, 1]
  data = tf.image.resize(data, [28, 28])
  return data


def predict(x):
  predictions = model(x)
  predictions = tf.nn.softmax(predictions)
  pred0 = predictions[0]
  label0 = np.argmax(pred0)
  return label0



def hello_world(request):
  """Responds to any HTTP request.
  Args:
      request (flask.Request): HTTP request object.
  Returns:
      The response text or any set of values that can be turned into a
      Response object using
      `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
  """
  # request_file = request.files.get("file")

  try:
    image_bytes = request.files['file']
    image_bytes = image_bytes.read()
    pillow_img = Image.open(io.BytesIO(image_bytes)).convert('L')
    tensor = transform_image(pillow_img)
    prediction = predict(tensor)
    data = {"prediction": int(prediction)}
    return jsonify(data)
  except Exception as e:
    return jsonify({"error": str(e)})

  return "OK"