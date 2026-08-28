import boto3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

import pandas as pd
from time import time
import re
import io

import json
import os
import sys
import re
from flask import Flask, request, jsonify


cleanup_re = re.compile('[^a-z]+')
tmp = '/tmp/'

app = Flask(__name__)

def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

@app.route('/', methods=['POST'])
def cleanup_main():
    json_from_request = request.json   # parse JSON body

    latencies = {}
    timestamps = {}
    
    timestamps["starting_time"] = time()
    
    dataset_bucket = json_from_request.get("dataset_bucket") #input_bucket
    dataset_object_key = json_from_request.get("dataset_object_key") #object_key
    model_object_key = json_from_request.get("model_object_key")# example : lr_model.pk
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

    start = time()
    obj = s3_client.get_object(Bucket=dataset_bucket, Key=dataset_object_key)
    download_data = time() - start
    latencies["download_data"] = download_data
    df = pd.read_csv(io.BytesIO(obj['Body'].read()))

    start = time()
    df['train'] = df['Text'].apply(cleanup)

    tfidf_vector = TfidfVectorizer(min_df=100).fit(df['train'])

    train = tfidf_vector.transform(df['train'])

    model = LogisticRegression()
    model.fit(train, df['Score'])
    function_execution = time() - start
    latencies["function_execution"] = function_execution

    model_file_path = tmp + model_object_key
    joblib.dump(model, model_file_path)

    start = time()
    s3_client.upload_file(model_file_path, model_bucket, model_object_key)
    upload_data = time() - start
    latencies["upload_data"] = upload_data
    timestamps["finishing_time"] = time()

    print("Function completed!")
    return jsonify({'statusCode': 200, "latencies": latencies, "timestamps": timestamps, "metadata": metadata})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))    