# This is not a part of the project, but is used for another project
from flask import Flask, request, render_template
import requests
import os
from vertexai.preview.generative_models import GenerativeModel
from dotenv import load_dotenv

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "random-developments-ccb662eb0a8f.json"

load_dotenv()

PROJECT_ID = os.getenv('PROJECT_ID')
LOCATION = os.getenv('LOCATION')

def get_gemini_response(input,image,prompt):
    model = GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input,image[0],prompt])
    return response.text
    

def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

input_prompt = """
You are an expert in understanding invoices.
You will receive input images as invoices &
you will have to answer questions based on the input image
"""

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('vision.html')

@app.route('/submit', methods=['GET'])
def submit():
    # Retrieve query and image from the form
    user_query = request.args.get('query')
    user_image = request.files['image']

    image_data = input_image_setup(user_image)
    response=get_gemini_response(input_prompt,image_data,user_query)

    return response

if __name__ == '__main__':
    app.run(debug=True)
