import boto3
import os
import pickle
import numpy as np
import torch
import rnn

from time import time


tmp = "/tmp/"

"""
Language
 - Italian, German, Portuguese, Chinese, Greek, Polish, French
 - English, Spanish, Arabic, Crech, Russian, Irish, Dutch
 - Scottish, Vietnamese, Korean, Japanese
"""


def main(event):
    latencies = {}
    timestamps = {}
    
    timestamps["starting_time"] = time()

    language = event['language']
    start_letters = event['start_letters']
    model_parameter_object_key = event['model_parameter_object_key']  # example : rnn_params.pkl
    model_object_key = event['model_object_key']  # example : rnn_model.pth
    model_bucket = event['model_bucket'] #input_bucket
    endpoint_url = event['endpoint_url']
    aws_access_key_id = event['aws_access_key_id']
    aws_secret_access_key = event['aws_secret_access_key']
    metadata = event['metadata']

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

    return {"latencies": latencies, "timestamps": timestamps, "metadata": metadata}