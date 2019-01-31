import azure.functions as func
from azure.storage.blob import BlockBlobService

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

import pandas as pd
import numpy as np 

import logging
from time import time
import re

FILE_NAME_INDEX = 2

cleanup_re = re.compile('[^a-z]+')
def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

def main(req: func.HttpRequest) -> func.HttpResponse:
    acc_name = req.params.get('account_name')
    acc_key = req.params.get('account_key')
    container_name = req.params.get('container_name')
    blob_name = req.params.get('blob_name')

    block_blob_service = BlockBlobService(account_name=acc_name, account_key=acc_key)
    
    download_path = "/tmp/" + blob_name
    block_blob_service.get_blob_to_path(container_name, blob_name, download_path)
    logging.info("Downloading blob to " + download_path)

    df = pd.read_csv(download_path)
    
    start = time()
    df['train'] = df['Text'].apply(cleanup)

    tfidf_vect = TfidfVectorizer(min_df=100).fit(df['train'])

    train = tfidf_vect.transform(df['train'])

    model = LogisticRegression()
    model.fit(train, df['Score'])

    latency = time() - start
    logging.info(latency)

    model_file_path = "/tmp/lr_model.pk"
    joblib.dump(model, model_file_path)

    block_blob_service.create_blob_from_path(container_name, model_file_path.split("/")[FILE_NAME_INDEX], model_file_path)
    return func.HttpResponse(str(latency))
