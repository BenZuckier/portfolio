from google.cloud import aiplatform

def pred(request):
    """
    Args:
        request (flask.Request): HTTP request object.
    """
    request_json = request.get_json(force=True)
    if PASSWORDCHECK_FAILURE: #redacted
        return

    def predict(
        instances, #the features to pass
        project: str , # redacted
        endpoint_id: str , # redacted
        location: str = "us-central1",
        api_endpoint: str = "us-central1-aiplatform.googleapis.com"
    ):
        client_options = {"api_endpoint": api_endpoint}
        # Initialize client that will be used to create and send requests.
        client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
        
        endpoint = client.endpoint_path(
            project=project, location=location, endpoint=endpoint_id
        )
       
        response = client.predict(
            endpoint=endpoint, instances=instances
        )
        
        predictions = response.predictions
        return predictions[0]

    if 'raw' in request_json:
        raw = request_json['raw']
        pred = predict(instances = [raw])
        return f'{pred}'
