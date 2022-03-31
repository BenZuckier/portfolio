from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from google.cloud import aiplatform
def pred(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    def predict(
        instances,
        project:str= ,  # redacted
        endpoint_id:str= , # redacted
        location:str="us-central1",
        api_endpoint:str="us-central1-aiplatform.googleapis.com"
        
    ):
        
        # The AI Platform services require regional API endpoints.
        client_options = {"api_endpoint": api_endpoint}
        # Initialize client that will be used to create and send requests.
        client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
        # The format of each instance should conform to the deployed model's prediction input schema.
        endpoint = client.endpoint_path(
            project=project, location=location, endpoint=endpoint_id
        )
        
        response = client.predict(
            endpoint=endpoint, instances=instances
        )
        # The predictions are a google.protobuf.Value representation of the model's predictions.
        predictions = response.predictions
        return predictions[0]

    headers = { # need to be enabled for the "frontend only" interface
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST'
    }
    request_json = request.get_json(force=True)
    if 'v' not in request_json or request_json['v'] != :  # redacted
        return 
    if 'twit' in request_json: # a tweet
        raw = request_json['twit'] # get tweet 
        predi = predict(instances = [raw]) # run prediction
        return (f'{predi}',200,headers) # response