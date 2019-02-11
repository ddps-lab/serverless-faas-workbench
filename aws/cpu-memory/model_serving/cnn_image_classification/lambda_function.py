import boto3
from tensorflow.python.keras.preprocessing import image
from tensorflow.python.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
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
    model_bucket = event['model_bucket']
    model_key = event['model_key']
    input_bucket = event['input_bucket']
    input_key = event['input_key']

    file_path = '/tmp/' + model_key
    s3_client.download_file(model_bucket, model_key, file_path)
    
    download_path = '/tmp/'+input_key
    s3_client.download_file(input_bucket, input_key, download_path)
        
    latency, result = predict(download_path)
        
    _tmp_dic = {x[1]: {'N': str(x[2])} for x in result[0]}
        
    print(latency)
    print(_tmp_dic)

    return latency
