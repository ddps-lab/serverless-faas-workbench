import boto3
import os
import pickle
import numpy as np
import torch
import rnn

from time import time


s3_client = boto3.client('s3')
tmp = "/tmp/"

"""
Language
 - Italian, German, Portuguese, Chinese, Greek, Polish, French
 - English, Spanish, Arabic, Crech, Russian, Irish, Dutch
 - Scottish, Vietnamese, Korean, Japanese
"""


def lambda_handler(event, context):
    language = event['language']
    start_letters = event['start_letters']

    model_parameter_object_key = event['model_parameter_object_key']  # example : rnn_params.pkl
    model_object_key = event['model_object_key']  # example : rnn_model.pth
    model_bucket = event['model_bucket']

    # Load pre-processing parameters
    # Check if model parameters are available
    parameter_path = tmp + model_parameter_object_key
    if not os.path.isfile(parameter_path):
        s3_client.download_file(model_bucket, model_parameter_object_key, parameter_path)

    with open(parameter_path, 'rb') as pkl:
        params = pickle.load(pkl)

    all_categories = params['all_categories']
    n_categories = params['n_categories']
    all_letters = params['all_letters']
    n_letters = params['n_letters']

    # Check if models are available
    # Download model from S3 if model is not already present
    model_path = tmp + model_object_key
    if not os.path.isfile(model_path):
        s3_client.download_file(model_bucket, model_object_key, model_path)

    rnn_model = rnn.RNN(n_letters, 128, n_letters, all_categories, n_categories, all_letters, n_letters)
    rnn_model.load_state_dict(torch.load(model_path))
    rnn_model.eval()

    start = time()
    output_names = list(rnn_model.samples(language, start_letters))
    latency = time() - start

    return {'latency': latency, 'predict': output_names}
