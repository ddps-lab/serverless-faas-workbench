import boto3
import os
import pickle
import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
from time import time

import rnn

BUCKET_NAME = "kmu-serverless-lambda-model"
s3_client = boto3.client('s3')

# Load preprocessing parameters
if not os.path.isfile('/tmp/rnn_params.pkl'):
    s3_client.download_file(BUCKET_NAME, 'rnn_params.pkl', '/tmp/rnn_params.pkl')
with open('/tmp/rnn_params.pkl', 'rb') as pkl:
    params = pickle.load(pkl)
all_categories = params['all_categories']
n_categories = params['n_categories']
all_letters = params['all_letters']
n_letters = params['n_letters']

# Check if models are available
# Download model from S3 if model is not already present
if not os.path.isfile('/tmp/rnn_model.pth'):
    s3_client.download_file(BUCKET_NAME, 'rnn_model.pth', '/tmp/rnn_model.pth')
rnn_model = rnn.RNN(n_letters, 128, n_letters, n_categories=n_categories)
rnn_model.load_state_dict(torch.load("/tmp/rnn_model.pth"))
rnn_model.eval()

def inputTensor(line):
    tensor = torch.zeros(len(line), 1, n_letters)
    for li in range(len(line)):
        letter = line[li]
        tensor[li][0][all_letters.find(letter)] = 1
    return tensor

def categoryTensor(category):
    li = all_categories.index(category)
    tensor = torch.zeros(1, n_categories)
    tensor[0][li] = 1
    return tensor

# Sample from a category and starting letter
def sample(category, start_letter='A'):
    category_tensor = Variable(categoryTensor(category))
    input = Variable(inputTensor(start_letter))
    hidden = rnn_model.initHidden()

    output_name = start_letter

    max_length=20
    for i in range(max_length):
        output, hidden = rnn_model(category_tensor, input[0], hidden)
        topv, topi = output.data.topk(1)
        topi = topi[0][0]
        if topi == n_letters - 1:
            break
        else:
            letter = all_letters[topi]
            output_name += letter
        input = Variable(inputTensor(letter))

    return output_name

# Get multiple samples from one category and multiple starting letters
def samples(category, start_letters='ABC'):
    for start_letter in start_letters:
        yield sample(category, start_letter)

"""
Language
 - Italian, German, Portuguese, Chinese, Greek, Polish, French
 - English, Spanish, Arabic, Crech, Russian, Irish, Dutch
 - Scottish, Vietnamese, Korean, Japanese
"""
def lambda_handler(event, context):
    language = event['language']
    start_letters = event['start_letters']
    start = time()
    output_names = list(samples(language, start_letters))
    latency = time() - start
    print(output_names)
    print(latency)
    return latency
