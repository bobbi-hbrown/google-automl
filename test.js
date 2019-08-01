
const projectId = 'sensible';
const computeRegion = 'us-central1';
const modelId = 'IOD4748957846131965952';

//Imports the Google Cloud Automl library
const { AutoMlClient } = require('@google-cloud/automl').v1beta1;

// Instantiates a client
const automlClient = new AutoMlClient({
  projectId: projectId,
  keyFilename: '/Users/rholding-brown/Documents/sensible-automl/service-account.json'
});
async function deployModel() {
  // Get the full path of the model.
  const modelFullId = automlClient.modelPath(
    projectId,
    computeRegion,
    modelId
  );

  console.log(modelFullId);

  // Deploy a model with the deploy model request.
  const [operation] = await automlClient.deployModel({ name: modelFullId });

  const [response] = await operation.promise();
  console.log(`Deployment Details:`);
  console.log(` Name: ${response.name}`);
  console.log(` Done: ${response.done}`);


}

async function undeployModel() {

  // Get the full path of the model.
  const modelFullId = automlClient.modelPath(
    projectId,
    computeRegion,
    modelId
  );

  console.log(modelFullId);
  try {
    // Deploy a model with the deploy model request.
    const [operation] = await automlClient.undeployModel({ name: modelFullId });
    const [response] = await operation.promise();
    for (const element of response) {
      console.log(`Undeployment Details:`);
      console.log(`\tName: ${element.name}`);
      console.log(`\tMetadata:`);
      console.log(`\t\tType Url: ${element.metadata.typeUrl}`);
      console.log(`\tDone: ${element.done}`);
    }
  } catch (e) {
    console.error(e)
  }
}

deployModel();