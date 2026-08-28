import boto3
from time import time
import pickle
import torch
import rnn
import json
import os
import sys
import re
from flask import Flask, request, jsonify

from time import time


tmp = "/tmp/"

app = Flask(__name__)

"""
Language
 - Italian, German, Portuguese, Chinese, Greek, Polish, French
 - English, Spanish, Arabic, Crech, Russian, Irish, Dutch
 - Scottish, Vietnamese, Korean, Japanese
"""

@app.route('/', methods=['POST'])
def rnn_generate():
    json_from_request = request.json   # parse JSON body

    latencies = {}
    timestamps = {}
    
    timestamps["starting_time"] = time()

    language = json_from_request.get("language")
    start_letters = json_from_request.get("start_letters")
    model_parameter_object_key = json_from_request.get("model_parameter_object_key")  # example : rnn_params.pkl
    model_object_key = json_from_request.get("model_object_key") # example : haarcascade_frontalface_default.xml
    model_bucket = json_from_request.get("model_bucket") # input_bucket as well
    endpoint_url = json_from_request.get("endpoint_url")
    aws_access_key_id = json_from_request.get("aws_access_key_id")
    aws_secret_access_key = json_from_request.get("aws_secret_access_key")
    metadata = json_from_request.get("metadata", None)

    s3_client = boto3.client('s3',
                    endpoint_url=endpoint_url,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key)#,                                                                                                                                                                                                                                                                                                            
                    #config=Config(signature_version='s3v4'),                                                                                                                                                                                                                                                                                                                 
                    #region_name='us-east-1')  

    # Check if models are available
    # Download model from S3 if model is not already present
    parameter_path = tmp + model_parameter_object_key
    model_path = tmp + model_object_key

    start = time()

    if not os.path.isfile(parameter_path):
        s3_client.download_file(model_bucket, model_parameter_object_key, parameter_path)

    if not os.path.isfile(model_path):
        s3_client.download_file(model_bucket, model_object_key, model_path)

    download_data = time() - start
    latencies["download_data"] = download_data

    start = time()

    with open(parameter_path, 'rb') as pkl:
        params = pickle.load(pkl)

    all_categories = params['all_categories']
    n_categories = params['n_categories']
    all_letters = params['all_letters']
    n_letters = params['n_letters']

    rnn_model = rnn.RNN(n_letters, 128, n_letters, all_categories, n_categories, all_letters, n_letters)
    rnn_model.load_state_dict(torch.load(model_path))
    rnn_model.eval()

    output_names = list(rnn_model.samples(language, start_letters))

    latency = time() - start
    latencies["function_execution"] = latency
    timestamps["finishing_time"] = time()

    print("Function completed!")    
    return jsonify({'statusCode': 200, "latencies": latencies, "timestamps": timestamps, "metadata": metadata})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))    