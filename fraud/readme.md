# Fraud Model and Cloud Deployment

## Overview

### Technologies

Flask, Google Apps Script, Google Cloud Functions (Serverless Computing), Google Sheets, Google Vertex AI (Cloud ML), JavaScript, Jupyter, Numpy, Pandas, Python, Scikit Learn (ML libraried including onehot encoder), XGB (Gradient Boosting ML Model)

### Video Explanation and Demo

Full explanation and demo [here](https://youtu.be/qIu0sl1VJWE). I think this is the best and easiest way to consume this demo.

### Just Demo

Here's a quick demo (unmute the audio!) of the frontend and model in action, since the Sheet isn't designed to be made public and shared (edit access etc.).

https://user-images.githubusercontent.com/39951657/160971676-1415e59a-b83e-4d10-a23d-da32538025bb.mp4

### Explanation

This is an XGB model to predict credit card fraud from [this](https://www.kaggle.com/competitions/ieee-fraud-detection/overview) dataset/competition on Kaggle. It is trained, exported and then uploaded as a model to Google Cloud's VertexAI. An internal endpoint is created pointing to the model and is made available on the internet using a Google Cloud Function which takes in a prediction or predictions and sends back a response of the fraud probability. The "frontend" is a Google Sheets sheet with an AppsScript function making requests to the Cloud Function.

## Files

There are two folders here:

1. [testing](testing/) has EDA and basic model construction, used while exploring and iterating before moving on to the next section.

1. [prod](prod/) has the code to actually export the model, run it in the cloud, and connect the frontend to everything. There are three folders within:

    1. [train](prod/train/) has a python script [train.py](prod/train/train.py) to make and export the model(s), found in the [models](prod/train/models) folder, which is actually run by a Jupyter [notebook](prod/train/Fraud_Model_Productionize.ipynb) since this was originally a Colab or hosted as VertexAI workbench.

    1. [cloud_function](prod/cloud_function/) has the Cloud Function Python [app](prod/cloud_function/main.py) which runs predictions on the model.

    1. [app_script](prod/app_script/) has the AppsScript [code](prod/app_script/Code.gs) to link to the Google Sheet used as a frontend as well as the sample data used in my demo, a copy of which can be found [here](https://docs.google.com/spreadsheets/d/1zpHGlI8lWm67PrrTzC5Bhgp6VAIiUFwth2xPnq5Aa2Y/edit?usp=sharing).

## Detailed Flow

### Frontend: Sheets

The frontend is on Google Sheets. The type of data (especially since it’s so big and there are so many features to tweak but we still want to be able to change whichever of them we want) lends itself very well to spreadsheet representation.
The input sheet is where the user changes the inputs to the model which both triggers the whole thing to run and shows the output below. I think it’s very simple and anyone could use it. 
There are also sheets on the bottom with samples of fraud and not fraud that the model has not seen. 
The frontend is actually responsible for changing the color of the FRAUD or NOT FRAUD cells to red and green based on the prediction probability cell.
If the user modifies any values, then it triggers the script on the following:

### Trigger: Apps Script

Google apps script! On value edit it triggers the function which pulls in the input row from the sheet. Then it makes an API call to the next stage with those data. When it gets the response it posts it to a cell in the sheet and then either highlights FRAUD or NOT FRAUD (color coded!) in the sheet.

### API “Hub”: Cloud Functions

I have a cloud function API which a normal person can call that basically acts as a foil for the actual ML AI Endpoint that is too hard to call for a normal human as we’ll see in a bit. This also gives us extra flexibility if we wanted to call more than one model or preprocess the data. We can basically do whatever we want in this function which is cool. It’s also fairly loosely coupled with the other stages so we can pretty easily swap out what model it calls or what else it does etc. 
Since cloud functions is running on the google cloud, it has authentication built in so we don’t have to worry as much about the Vertex AI endpoint auth. Also since it’s a “serverless” API call, we don’t have our model running all the time and if we decide not to actually call the model then we don’t waste more expensive compute credits. It’s connected to the Vertex AI endpoint and just taken in a POST request with “raw” field of a 2D array of features, makes the endpoint call to the Vertex model and sends back the a string of the first prediction value from the model

### Model: Vertex AI
I
 have my model on Vertex AI but it has its own endpoint that you need the special google credentials for, this was both too annoying to use on its own (especially with javascript/appscript) and not flexible enough. That’s why I “wrapped” it with the other stuff above. I could have used the Vertex pipelines or Kubeflow pipelines but the documentation was a little overwhelming for the training and for the actual evaluation (especially how to preprocess the eval input etc). 
So in the end I used their import model option with a premade container. Essentially you can upload one of Tensorflow, scikit, or XGB models and select the right environment (like XGB 1.4) which automatically sets up the container for the model etc. Just need to get the naming convention right (for example XGB is model.bst) Then once the model is imported into Vertex you can make an endpoint for it which just has it take in a json field called “instances” of the 2D array mentioned above. It just passes this right to the model to evaluate and returns the predicted probability result. 

### Model training

I could have used another cloud function to run the training script on the training data to train the model (or really have done it natively in vertex ai) but instead I did it locally on my machine (with my nice GPU that makes it so much faster lol) and uploaded it to vertex as above.

Note: I made sure when training the model that I train test split the data and didn’t show the test data to the model. I saved a portion of that training data and uploaded it as the examples in the sheets frontend above. 

