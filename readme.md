Sensible AutoML Object Detection Pipeline

This repo contains all files needed for implementing an end-to-end machine learning pipeline, with training and prediction hosted on Google's AutoML service. This includes 
a script for taking screenshots of dimension 1200 x 3000 from news websites, which are then uploaded to gs://sensible-ml-pipeline/data/images/png/ on the hour at bi-hourly intervals 
(starting from 24:00 UTC). // Could this script also be moved to a cloud function?

Another python script, hosted on a cloud function, is then triggered upon the event of new images landing in the Cloud Storage bucket. This script contains the function get_prediction()
which calls AutoML's PredictionServiceClient() to serve new predictions on the screenshots. After each image is processed, 