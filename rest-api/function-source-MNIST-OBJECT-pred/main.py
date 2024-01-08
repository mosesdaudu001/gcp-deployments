import numpy
import tensorflow
import io

from google.cloud import storage
from tensorflow.keras.layers import Dense, Flatten, Conv2D
from tensorflow.keras import Model
from PIL import Image
from flask import Flask, request, jsonify

# We keep model as global variable so we don't have to reload it in case of warm invocations
model = None

class CustomModel(Model):
  def __init__(self):
    super(CustomModel, self).__init__()
    self.conv1 = Conv2D(32, 3, activation='relu')
    self.flatten = Flatten()
    self.d1 = Dense(128, activation='relu')
    self.d2 = Dense(10, activation='softmax')

  def call(self, x):
    x = self.conv1(x)
    x = self.flatten(x)
    x = self.d1(x)
    return self.d2(x)

def download_blob(bucket_name, source_blob_name, destination_file_name):
  """Downloads a blob from the bucket."""
  storage_client = storage.Client()
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(source_blob_name)

  blob.download_to_filename(destination_file_name)

  print('Blob {} downloaded to {}.'.format(
    source_blob_name,
    destination_file_name))

def handler(request):
  global model
  class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat','Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

  # Model load which only happens during cold starts
  if model is None:
    download_blob('moses-daudu-bucket', 'models/fashion_mnist_weights.index', '/tmp/fashion_mnist_weights.index')
    download_blob('moses-daudu-bucket', 'models/fashion_mnist_weights.data-00000-of-00001', '/tmp/fashion_mnist_weights.data-00000-of-00001')
    model = CustomModel()
    model.load_weights('/tmp/fashion_mnist_weights')

  # download_blob('moses-daudu-bucket', 'models/test.png', '/tmp/test.png')
  if request.method == "POST":
    img_file = request.files['file']
    if img_file is None or img_file.filename == "":
      return jsonify({"error": "no file"})

    try:
      image_bytes = img_file.read()
      pillow_img = Image.open(io.BytesIO(image_bytes)).convert('L')
      input_np = (numpy.array(pillow_img)/255)[numpy.newaxis,:,:,numpy.newaxis]
      predictions = model.call(input_np)
      prediction = class_names[numpy.argmax(predictions)]
      data = {"prediction": str(prediction)}
      return jsonify(data)
    except Exception as e:
      return jsonify({"error": str(e)})

    return "OK"



    # image = numpy.array(image_content)
    
    # input_np = (numpy.array(Image.open('/tmp/test.png'))/255)[numpy.newaxis,:,:,numpy.newaxis]
    # predictions = model.call(input_np)
    # print(predictions)
    # print("Image is "+class_names[numpy.argmax(predictions)])
    
    # return class_names[numpy.argmax(predictions)]