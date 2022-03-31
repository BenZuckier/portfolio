import json
from google.cloud import aiplatform

PROJECT_ID = "constant-rig-331503" 
REGION = "us-central1"       
PIPELINE_ROOT = 'gs://dsa-ross/pipeline_root/'


def run_pipe(request):
   """Processes the incoming HTTP request.

   Args:
     request (flask.Request): HTTP request object.

   Returns:
     The response text or any set of values that can be turned into a Response
     object using `make_response
     <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
   """

   # decode http request payload and translate into JSON object
   request_str = request.data.decode('utf-8')
   request_json = json.loads(request_str)

   pipeline_spec_uri = request_json['pipeline_spec_uri']
  #  gs://dsa-ross/dsa-rossman-pipe

   aiplatform.init(
       project=PROJECT_ID,
       location=REGION,
   )

   job = aiplatform.PipelineJob(
       display_name=f'dsa-rossman',
       template_path=pipeline_spec_uri,
       pipeline_root=PIPELINE_ROOT,
      #  enable_caching=False,
      #  parameter_values=parameter_values
   )

   job.run(sync=False)
   return "Job submitted"