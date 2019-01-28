import boto3
from tensorflow.python import keras
from tensorflow.python.keras.preprocessing import image
from tensorflow.python.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import io
import os
from PIL import Image
import h5py
import uuid
from time import time

from squeezenet import SqueezeNet

s3_client = boto3.client('s3')

def predict(img_local_path):
    start = time()
    model = SqueezeNet(weights='imagenet')
    img = image.load_img(img_local_path, target_size=(227, 227))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    res = decode_predictions(preds)
    latency = time() - start
    return latency, res

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)

    s3_client.download_file(bucket, key, download_path)
    s3_client.download_file('kmu-serverless-deeplearning-model', 'squeezenet_weights_tf_dim_ordering_tf_kernels.h5', '/tmp/squeezenet_weights_tf_dim_ordering_tf_kernels.h5')
    lantecy, result = predict(download_path)
    _tmp_dic = {x[1]: {'N': str(x[2])} for x in result[0]}
    print(latency)
    print(_tmp_dic)

    return latency
