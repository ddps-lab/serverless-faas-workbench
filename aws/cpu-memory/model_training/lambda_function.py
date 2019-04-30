import boto3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

import pandas as pd
from time import time
import re

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

cleanup_re = re.compile('[^a-z]+')
tmp = '/tmp/'


def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence


def lambda_handler(event, context):
    input_bucket = event['input_bucket']
    object_key = event['object_key']
    model_bucket = event['model_bucket']
    model_object_key = event['model_object_key']  # example : lr_model.pk

    df = pd.read_csv('s3://'+input_bucket+object_key)

    start = time()
    df['train'] = df['Text'].apply(cleanup)

    tfidf_vector = TfidfVectorizer(min_df=100).fit(df['train'])

    train = tfidf_vector.transform(df['train'])

    model = LogisticRegression()
    model.fit(train, df['Score'])
    latency = time() - start

    model_file_path = tmp+model_object_key
    joblib.dump(model, model_file_path)

    s3.Object(model_bucket, model_object_key).load()

    return latency
