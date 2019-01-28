import boto3
import os
import sys
import uuid
from time import time
from PIL import Image, ImageFilter

import ops

s3_client = boto3.client('s3')

FILE_NAME_INDEX = 2

def image_processing(file_name, image_path):
    path_list = []
    start = time()
    with Image.open(image_path) as image:
        tmp = image
        path_list += ops.flip(image, file_name)
        path_list += ops.rotate(image, file_name)
        path_list += ops.filter(image, file_name)
        path_list += ops.gray_scale(image, file_name)
        path_list += ops.resize(image, file_name)

    latency = time() - start
    return latency, path_list

def lambda_handler(event, context):
    latency_list = []

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)

        s3_client.download_file(bucket, key, download_path)

        file_name = key
        
        latency, path_list = image_processing(file_name, download_path)
        
        for upload_path in path_list:
            s3_client.upload_file(upload_path, 'result-image-data-augmentation', upload_path.split("/")[FILE_NAME_INDEX])

        latency_list.append(latency)

    return latency_list
