import os
import sys
import time
import requests
import json
import datetime
from google.cloud import storage
from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2

from google.cloud import storage
from google.oauth2 import service_account


project_id = 'sensible'
bucket_name = 'sensible-screenshots'
model_id = 'IOD4748957846131965952'
current_directory = os.path.dirname(os.path.realpath(__file__))
websites_file = current_directory + "/websites.json"
service_account = current_directory + "/service-account.json"
date_time = "{date:%Y-%m-%d--%H%M}".format(date=datetime.datetime.now())
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = current_directory + \
    "/service-account.json"


# 'content' is base-64-encoded image data.
# 'data' - dict - event payload
# 'context' - metadata

def predict_on_trigger():
  '''This function is triggered whenever new files are uploaded to GCS sensible-screenshots/ bucket
  1) deploy model function
  2) wait for succesful response
  3) load websites from json file
  4) take screenshots
  5) download screenshots to temp local storage
  6) call getPrediction
  7) wait for all prediction data to be returned
  8) undeploy model
  '''

  try:
    check_deployed_status()
    # deploy_model()
    # download_blob(image_full_path, project_id, destination_file_name)
    # websites = load_websites()
    # loop_websites(websites)

  except Exception as e:
    print(e)


'''
  try:
    get_prediction(destination_file_name, project_id, model_id, image_name)
  except Exception as e:
    print(e)
'''


def check_deployed_status():

  headers = {
  "Authorization": "Bearer $(gcloud auth application-default print-access-token)",
  }

  try:
    response = requests.get(
        "https://automl.googleapis.com/v1beta1/projects/sensible/locations/us-central1/models/IOD4748957846131965952", headers=headers)
    print(response)
  except Exception as e:
    print(e)


def deploy_model():

	headers = {
		"Content-Type": "application/json",
    "Authorization": "Bearer $(gcloud auth application-default print-access-token)"
	}
	data = {'imageObjectDetectionModelDeploymentMetadata': {'nodeCount': 2}}

	model_url = "https://automl.googleapis.com/v1beta1/projects/sensible/locations/us-central1/models/IOD4748957846131965952:deploy"

	response = requests.post(model_url, headers=headers, data=data)

  if "OperationMetadata" in response["metadata"]["@type"]:
    print("model deployment has begun")
  else:
    print("model deployment failed!")
    print(response)

def download_blob(image_full_path, project_id, destination_file_name):
  # Downloads a blob from the bucket.
  source_blob_name = image_full_path
  
  try:
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    
    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
      source_blob_name,
      destination_file_name))

  except Exception as e:
    print('Download file to Cloud Function /tmp dir failed: {}'.format(e))

# Function to load websites from a separate file
def load_websites():
    with open(websites_file) as config:
        data = json.load(config)
    return data

# Function to loop through all websites loaded from JSON file and call makeScreenshot function
def loop_websites(websites):
    for website in websites:
        make_screenshot(website)
    return

# Function to use Headless Chrome to take a screenshot of each website and upload to Cloud Storage
def make_screenshot(website):
    # Variables for this website
    domain = website["domain"]
    if "PRODUCTION" in os.environ:
        image_directory = "/tmp/images/" + website["name"]
        # Check to see if images folder exists and creates it if not
        if not os.path.exists("/tmp/images"):
            os.makedirs("/tmp/images")
    else:
        image_directory = "images/" + website["name"]
        file_name = date_time + "--" + website["name"] + ".png"
        image = image_directory + "/" + file_name
        window_size = website["width"] + "," + website["height"]
        chromedriver_path = "/usr/local/bin/chromedriver"
    
    # Check to see if website directory exists and create it if it doesn't
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)

    # Chrome Options
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--window-size=%s" % window_size)
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    # Open Chrome with options and go to URL
    driver = webdriver.Chrome(chrome_options=options, executable_path=chromedriver_path)
    driver.get(domain)

    # Take screenshot of page
    driver.save_screenshot(image)

    # Close Chrome
    driver.close()

    # Push file to Cloud Storage
    push_file_to_cloud_storage(image)

    return

# Function to push image file to Google Cloud Storage
def push_file_to_cloud_storage(file_name):
    credentials = service_account.Credentials.from_service_account_file(service_account)

    # Connect to project
    client = storage.Client(credentials=credentials, project=project_id)

    # Connect to bucket
    bucket = client.get_bucket(bucket_name)

    # Upload file
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)

    # Delete screenshot
    delete_screenshot(file_name)

    return


def get_prediction(destination_file_name, project_id, model_id, image_name):

  score_threshold = '0.5'
  
  try:
    with open(destination_file_name, 'rb') as ff:
      content = ff.read()

    print('Beginning prediction for image {}'.format(image_name))
    prediction_client = automl_v1beta1.PredictionServiceClient()
    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'image': {'image_bytes': content }}
    params = {"score_threshold": score_threshold}
    request = prediction_client.predict(name, payload, params)
    print('Prediction complete for image {}'.format(image_name))
    print("Prediction results:")
    print(request)
    print(request.payload)
    # for result in request.payload:

      # print("Predicted class name: {}".format(result.display_name))
      # print("Predicted class score: {}".format(result.classification.score))

  except Exception as e:
    retries = 0
    if e == 'Model is warming up. Please try again later.':
      while retries < 5:
        time.sleep(180)
        retries += 1
        continue
      if retries == 5:
        print('This warmup delay can occur when you initially query your model, or when you make a request from a model that has not been queried recently')
    else:
      print(e)



sample curl deploy response

{
  "name": "projects/714556677880/locations/us-central1/operations/IOD3078131180470534144",
  "metadata": {
    "@type": "type.googleapis.com/google.cloud.automl.v1beta1.OperationMetadata",
    "createTime": "2019-05-15T10:24:32.685317Z",
    "updateTime": "2019-05-15T10:24:32.685317Z",
    "deployModelDetails": {}
  }
}





    headers = {
    "Authorization": "Bearer $(gcloud auth application-default print-access-token)",
    }

    data = {}

    model_url = "https://automl.googleapis.com/v1beta1/projects/sensible/locations/us-central1/models/IOD4748957846131965952"


    curl -X GET \
      -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
      https://automl.googleapis.com/v1beta1/projects/sensible/locations/us-central1/models/IOD4748957846131965952
      -d '{}'

'''

predict_on_trigger()
