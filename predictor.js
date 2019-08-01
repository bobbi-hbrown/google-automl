// Script to programatically deploy AutoML model, download new images to /tmp dir, run online predictions on new images, then undeploy model when complete

const projectId = 'sensible';
const computeRegion = 'us-central1';
const modelId = 'IOD4748957846131965952';

//Imports the Google Cloud Automl library
const {AutoMlClient} = require('@google-cloud/automl').v1beta1;
const {Storage} = require('@google-cloud/storage');

exports.main=(req, res) => {
    predictOnTrigger(res);
};


async function predictOnTrigger (res) {
    deployModel();
    destFileName = await downloadBlob(res);

    try {
        const modelFullId = await getModelFullId()
        const response.done = await deployModel(modelFullId)
        const valueC = await functionC(valueB)
        return await functionD(valueC)
      } catch(e) {
        logger.error(e)
      }
    
}

/*
Structure needed for function calls:
move get model full id into own function
await deploy model - pass fullId into this
- i don't want to wait for it to finish deploying before continuing to move onto download blob - return destFileName
when downloaded, move onto getPrediction - pass in destFileName - for this i need model deployed
when complete, undeploy model - make sure it is fully undeployed
*/

async function getModelFullId() {

    try {
        //Instantiate AutoML client
         const automlClient = new AutoMlClient();

        // Get the full path of the model.
        const modelFullId = automlClient.modelPath(
            projectId,
            computeRegion,
            modelId
        );

        console.log(modelFullId);
        return modelFullId;

        } catch(e) {
            console.error(e)
        }

}

async function deployModel() {

    try {
        // Deploy a model with the deploy model request.
        const [operation] = await automlClient.deployModel({name: modelFullId});

        // Log response to stackdriver
        const [response] = await operation.promise();
        console.log(`Deployment Details:`);
        console.log(` Name: ${response.name}`);
        console.log(` Metadata:`);
        console.log(`   Type Url: ${response.metadata.typeUrl}`);
        console.log(` Done: ${response.done}`);  

    } catch(e) {
        console.log("Model failed to deploy")
        console.error(e)
    }
}

async function downloadBlob (res) {
    // Instantiate a storage client
    const storage = new Storage({
        projectId: projectId
    });

    // Variables specifying from where to download
    // res['resource']['name'] format projects/_/buckets/sensible-screenshots/objects/images/bbc/2018-07-20--1200--bbc.png
    const imageName = res['resource']['name']
                      .split('/')[7]; // 'format 2018-07-20--1200--bbc.png'
   console.log(imageName);

    const bucketName = 'sensible-screenshots'; 

    const srcFileName = res['resource']['name']
                        .split('/')
                        .slice(5)
                        .join("/"); // format images/bbc/2019-04-17--0800--bbc.png

            
    console.log(srcFileName);

    const destFileName = '/tmp/' + imageName;

    const options = {
      // The path to which the file should be downloaded, e.g. "./file.txt"
      destination: destFileName
    };
    
    try {
        // Downloads the file
        await storage
        .bucket(bucketName)
        .file(srcFileName)
        .download(options);

        console.log(
          `gs://${bucketName}/${srcFileName} downloaded to ${destFileName}.`
        );
        
        deployModel(projectId, computeRegion, modelId, destFileName);
        return imageName;
        return destFileName;

    } catch(e) {
      console.error(e)
    }
}

async function getPrediction(destFileName, modelFullId) {
    // Instantiates a client
    const predictionServiceClient = new PredictionServiceClient();

    const fs = require(`fs`);

    // Read the file content for prediction.
    const content = fs.readFileSync(destFileName, `base64`);
    let params = {scoreThreshold: '0.5'};

    if (scoreThreshold) {
        params = {
        scoreThreshold: scoreThreshold,
        };
    }

    // Set the payload by giving the content and type of the file.
    const payload = {
        image: {
        imageBytes: content,
        },
    };

    try {
        // params is additional domain-specific parameters.
        const [response] = await predictionServiceClient.predict({
            name: modelFullId,
            payload: payload,
            params: params,
        });

        console.log(`Prediction results:`);

        for (const result of response[0].payload) {
            console.log(`\nPredicted class name:  ${result.displayName}`);
            console.log(
            `Predicted class score:  ${result.imageObjectDetection.score}`
            );
        } 
        undeployModel(modelFullId);
    } catch(e) {
        console.error(e)
    }
}

async function undeployModel(modelFullId) {
    try {
        // Deploy a model with the deploy model request.
        const [operation] = await automlClient.undeployModel({name: modelFullId});
        const [response] = await operation.promise();
        for (const element of response) {
          console.log(`Undeployment Details:`);
          console.log(`\tName: ${element.name}`);
          console.log(`\tMetadata:`);
          console.log(`\t\tType Url: ${element.metadata.typeUrl}`);
          console.log(`\tDone: ${element.done}`);
        } 
      }  catch(e) {
        console.error(e)
    }
}
