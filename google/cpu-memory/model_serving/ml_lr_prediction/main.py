from google.cloud import storage
import gcsfs

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

import pandas as pd
import numpy as np

from time import time
import re

cleanup_re = re.compile('[^a-z]+')
def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

def download_blob(blob, download_path):
    blob.download_to_filename(download_path)
    print('Blob {} downloaded to {}.'.format(
        blob.name,
        download_path))

def function_handler(request):
    request_json = request.get_json(silent=True)
    x = request_json['input']
    dataset_bucket = request_json['dataset_bucket']
    dataset_blob_name = request_json['dataset_blob_name']
    model_bucket = request_json['model_bucket']
    model_blob_name = request_json['model_blob_name']
    
    storage_client = storage.Client()
    model_file_path = "/tmp/" + model_blob_name
    m_bucket = storage_client.get_bucket(model_bucket)
    m_blob = m_bucket.blob(model_blob_name)
    download_blob(m_blob, model_file_path)
    
    fs = gcsfs.GCSFileSystem(project='Serverless-faas-workbench')
    with fs.open(dataset_bucket+'/'+dataset_blob_name) as f:
        df = pd.read_csv(f)
    
        start = time()
        df['train'] = df['Text'].apply(cleanup)

        tfidf_vect = TfidfVectorizer(min_df=100).fit(df['train'])
        
        df_input = pd.DataFrame()
        df_input['x']  = [x]
        df_input['x'] = df_input['x'].apply(cleanup)
        X = tfidf_vect.transform(df_input['x'])
        
        model = joblib.load(model_file_path)
        y = model.predict(X)
        print(y)
        latency = time() - start
        print(latency)
        return "latency : " + str(latency)