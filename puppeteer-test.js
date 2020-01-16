// Script to programatically deploy AutoML model, download new images to /tmp dir, run online predictions on new images, then undeploy model when complete
const config = require('./config.json');
const projectId = config.projectId;
const computeRegion = config.computeRegion;
const modelId = config.modelId;
const currentDirectory = __dirname

const puppeteer = require("puppeteer");
const { AutoMlClient } = require('@google-cloud/automl').v1beta1;
const { Storage } = require('@google-cloud/storage');
const fs = require('fs');
var retries = 0;
const maxRetries = 5; // Number of times we want to retry taking screenshots if timeout error occurs
var numScreenshots = 0;

//Instantiate AutoML client
const automlClient = new AutoMlClient({
  projectId: "sensible",
  keyFilename: currentDirectory + "/service-account.json"
});

/*
  1) deploy model function >
  2) wait for succesful response >
  3) load websites from json file
  4) take screenshots
  5) download screenshots to temp local storage
  6) call getPrediction
  7) wait for all prediction data to be returned
  8) undeploy model
*/

getModelFullId = () => {

  try {
    // Get the full path of the model.
    const modelFullId = automlClient.modelPath(
      projectId,
      computeRegion,
      modelId
    );
    return modelFullId;
    console.log(modelFullId);
  } catch (e) {
    console.error(e)
  }

}

async function deployModel(modelFullId) {
  try {
    // Deploy a model with the deploy model request.
    console.log(modelFullId);

    function sleep(millis) {
      return new Promise(resolve => setTimeout(resolve, millis));
    }
    await sleep(9000);
    console.log("model deployed!");
    const [operation] = await automlClient.deployModel({ name: modelFullId });
    // Add log response to stackdriver
    const [response] = await operation.promise();
    console.log(`Deployment Details:`);
    console.log(` Name: ${response.name}`);
    console.log(` Done: ${response.done}`);

    loopWebsites();

  } catch (e) {
    if (e["details"] === "The model is already deployed.") {
      console.log("A");
      loopWebsites();
      console.log(1)
      console.log(e["details"]);
    } else {
      console.log("Model failed to deploy");
      console.error(e)
    }
  }
}

loadWebsites = () => {
  return new Promise(resolve => {
    fs.exists(currentDirectory + "/websites.json", function (exists) {
      if (exists) {

        fs.readFile(currentDirectory + "/websites.json", { encoding: "utf8" }, function (err, websitesList) {
          if (err) {
            console.log(err);
          }

          console.log("load websites");
          resolve(websitesList);
        })
      }
    });
  });
}

// Separate takeScreenshot into its own sync function

function screenshot(website, page, today) {
  imageName = website["name"];
  siteDomain = website["domain"];
  return new Promise((resolve) => {
    page.waitFor(20000);
    page.screenshot({ path: currentDirectory + "/images/" + imageName + today + ".png" });
    page.waitFor(20000);
  });
}

async function loopWebsites() {
  var websitesList = await loadWebsites();
  //var websitesList = websitesList.split(",")
  var websitesList = JSON.parse(websitesList);
  console.log(typeof websitesList);
  console.log(websitesList);
  console.log("loop websites");
  

  //this part of script needs to wait until first takeScreenshot loop is finished before starting next one
  websitesList.forEach(async function (website, browser) {
    var browser = await puppeteer.launch();
    var page = await browser.newPage(); //this needs to be waited for
    var siteUrl = website[""]
    await page.goto(siteDomain, { timeout: 0, waitUntil: 'networkidle0' }).then(
    await takeScreenshot(website, browser, page)).then(
        console.log(`Taking screenshot: ${website["name"]}`)).then(
        console.log(numScreenshots)).then( numScreenshots += 1 )
    //await browser.close(); it happens between 2nd and 3rd
  }
).then(
  console.log("all screenshots taken!")).then(
  await browser.close());

}

async function takeScreenshot(website, browser, page) {

  try {
    imageName = website["name"];
    siteDomain = website["domain"];
    dimensions = website["dimensions"];
    console.log(siteDomain);
    var today = new Date();
    //console.log("Puppeteer launched succesfully");
    await page.setViewport({ width: 1024, height: 3000 });
    
    await screenshot(website, page, today); //this is calling a synchronous function 
    await browser.close();
    console.log(`Screenshot taken: ${website["name"]}`);
    return;
  } catch (e) {
    console.error(e)
    
    console.log(typeof e);
    if ( e.includes("TimeoutError") ) {
      while (retries < maxRetries) {
        retries += 1;
        console.log(`Timeout ${n}`);
        takeScreenshot(website);
      } if (retries === maxRetries) {
        console.log(`Puppeteer has reached its limit of ${maxRetries} timeout errors. Check for internet connectivity issues or increase the value of maxRetries in the script.`);
        process.exitCode = 1;
        return process.exitCode;
      }
    } else {
      console.log("Screenshot failed!");
      console.error(e);
      process.exitCode = 1;
      return process.exitCode;
    }

    
  }
}

modelFullId = getModelFullId()
deployModel(modelFullId)
