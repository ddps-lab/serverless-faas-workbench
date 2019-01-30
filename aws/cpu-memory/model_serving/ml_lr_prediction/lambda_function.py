import boto3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

import pandas as pd
import numpy as np

from time import time
import os
import re

s3_client = boto3.client('s3')

if not os.path.isfile('/tmp/lr_model.pk'):
    s3_client.download_file("kmu-serverless-lambda-model", 'lr_model.pk', '/tmp/lr_model.pk')

cleanup_re = re.compile('[^a-z]+')
def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

def lambda_handler(event, context):
    x = event['input']
    df = pd.read_csv('s3://kmu-serverless-lambda-dataset/reviews0.csv')

    start = time()
    df_input = pd.DataFrame()
    df_input['x']  = [x]
    df_input['x'] = df_input['x'].apply(cleanup)

    df['train'] = df['Text'].apply(cleanup)
    tfidf_vect = TfidfVectorizer(min_df=100).fit(df['train'])
    print(len(tfidf_vect.get_feature_names()))
    X = tfidf_vect.transform(df_input['x'])

    model = joblib.load('/tmp/lr_model.pk')
    y = model.predict(X)
    print(y)
    latency = time() - start
    print(latency)
    return latency