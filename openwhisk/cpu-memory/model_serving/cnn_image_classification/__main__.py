import boto3
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import uuid
from time import time

from squeezenet import SqueezeNet

s3_client = boto3.client('s3')

tmp = "/tmp/"



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


def main(args):
    input_bucket = args['input_bucket']
    object_key = args['object_key']

    model_object_key = args['model_object_key']  # example : squeezenet_weights_tf_dim_ordering_tf_kernels.h5
    model_bucket = args['model_bucket']

    download_path = tmp + '{}{}'.format(uuid.uuid4(), object_key)
    s3_client.download_file(input_bucket, object_key, download_path)

    model_path = tmp + '{}{}'.format(uuid.uuid4(), model_object_key)
    s3_client.download_file(model_bucket, model_object_key, model_path)
    
    latency, result = predict(download_path)
        
    _tmp_dic = {x[1]: {'N': str(x[2])} for x in result[0]}

    return {"latency": latency}
