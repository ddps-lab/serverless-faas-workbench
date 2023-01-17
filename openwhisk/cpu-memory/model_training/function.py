import boto3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

import pandas as pd
from time import time
import re
import io

cleanup_re = re.compile('[^a-z]+')
tmp = '/tmp/'


def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence


def main(event):
    latencies = {}
    timestamps = {}
    
    timestamps["starting_time"] = time()
    
    dataset_bucket = event['dataset_bucket'] #input_bucket
    dataset_object_key = event['dataset_object_key'] #object_key
    model_bucket = event['model_bucket'] #output_bucket
    model_object_key = event['model_object_key']  # example : lr_model.pk
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

    return {"latencies": latencies, "timestamps": timestamps, "metadata": metadata}