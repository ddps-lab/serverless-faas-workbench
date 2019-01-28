import boto3
import botocore

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

import pandas as pd
import numpy as np
import uuid
from time import time
import re

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

cleanup_re = re.compile('[^a-z]+')
def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

def lambda_handler(event, context):
    #buckt = event['input_bucket']
    #key = event['key']
    df = pd.read_csv('s3://kmu-serverless-dataset/Reviews.csv')

    start = time()
    df['train'] = df['Text'].apply(cleanup)

    tfidf_vect = TfidfVectorizer(min_df=100).fit(df['train'])

    train = tfidf_vect.transform(df['train'])

    model = LogisticRegression()
    model.fit(train, df['Score'])

    latency = time() - start
    print(latency)
    model_file_path = "/tmp/lr_model.pk"
    joblib.dump(model, model_file_path)

    model_bucket = 'kmu-serverless-lambda-model'
    model_object_key = 'lr_model.pk'

    s3.Object(model_bucket, model_object_key).load()
    return latency