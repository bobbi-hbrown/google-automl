import sys, os, time
from google.cloud import storage
from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2

project_id = 'sensible'
bucket_name = 'sensible-screenshots'
model_id = 'IOD4748957846131965952'

# 'content' is base-64-encoded image data.
# 'data' - dict - event payload
# 'context' - metadata 

def predict_on_trigger(data, context):
  '''This function is triggered whenever new files are uploaded to GCS sensible-screenshots/ bucket'''

  image_name = data['id'].split('/')[3] # format 2019-04-18--0800--independent.png
  image_full_path = data['name'] # format images/bbc/2019-04-17--0800--bbc.png
  destination_file_name = "/tmp/" + image_name

  try:
    download_blob(image_full_path, project_id, destination_file_name)
  except Exception as e:
    print(e)

  try:
    get_prediction(destination_file_name, project_id, model_id, image_name)
  except Exception as e:
    print(e)

  try:
    upload_predictions(args):
  except:
    pass

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
    #for result in request.payload:
      #print("Predicted class name: {}".format(result.display_name))
      #print("Predicted class score: {}".format(result.classification.score))

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
  
  def upload_predictions(project_id):

  try:
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))
