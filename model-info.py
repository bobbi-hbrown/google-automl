import json
from google.cloud import automl_v1beta1 as automl
from google.cloud.automl_v1beta1 import enums


with open('config.json') as json_file:
    config = json.load(json_file)

project_id = config.project_id
compute_region = config.compute_region
model_id = config.model_id

client = automl.AutoMlClient()

# Get the full path of the model.
model_full_id = client.model_path(project_id, compute_region, model_id)

# Get complete detail of the model.
model = client.get_model(model_full_id)

# Retrieve deployment state.
if model.deployment_state == enums.Model.DeploymentState.DEPLOYED:
    deployment_state = "deployed"
else:
    deployment_state = "undeployed"

# Display the model information.
print("Model name: {}".format(model.name))
print("Model id: {}".format(model.name.split("/")[-1]))
print("Model display name: {}".format(model.display_name))
print("Image classification model metadata:")
print(
    "Training budget: {}".format(
        model.image_classification_model_metadata.train_budget
    )
)
print(
    "Training cost: {}".format(
        model.image_classification_model_metadata.train_cost
    )
)
print(
    "Stop reason: {}".format(
        model.image_classification_model_metadata.stop_reason
    )
)
print(
    "Base model id: {}".format(
        model.image_classification_model_metadata.base_model_id
    )
)
print("Model create time:")
print("\tseconds: {}".format(model.create_time.seconds))
print("\tnanos: {}".format(model.create_time.nanos))
print("Model deployment state: {}".format(deployment_state))