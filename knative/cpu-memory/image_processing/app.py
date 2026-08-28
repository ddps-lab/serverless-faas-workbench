import boto3
import uuid
from time import time
from PIL import Image
import json
import os
import sys
import re
from flask import Flask, request, jsonify
import ops


FILE_NAME_INDEX = 1

app = Flask(__name__)

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
    print("PATH_LIST", path_list)
    return latency, path_list

@app.route('/', methods=['POST'])
def image_processing_main():
    json_from_request = request.json   # parse JSON body

    latencies = {}
    timestamps = {}
    timestamps["starting_time"] = time()

    input_bucket = json_from_request.get("input_bucket")
    object_key = json_from_request.get("object_key")
    output_bucket = json_from_request.get("output_bucket")
    endpoint_url = json_from_request.get("endpoint_url")
    aws_access_key_id = json_from_request.get("aws_access_key_id")
    aws_secret_access_key = json_from_request.get("aws_secret_access_key")
    metadata = json_from_request.get("metadata", None)

    s3_client = boto3.client('s3',
                    endpoint_url=endpoint_url,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key)#,                                                                                                                                                                                                                                                                                                            
                    #config=Config(signature_version='s3v4'),                                                                                                                                                                                                                                                                                                                 
                    #region_name='us-east-1')   
    start = time()
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), object_key)
    s3_client.download_file(input_bucket, object_key, download_path)
    download_latency = time() - start
    latencies["download_data"] = download_latency

    image_processing_latency, path_list = image_processing(object_key, download_path)
    latencies["function_execution"] = image_processing_latency
    print("PATH_LIST OUTSIDE", path_list)

    start = time()
    for upload_path in path_list:
        s3_client.upload_file(upload_path, output_bucket, upload_path.split("/")[FILE_NAME_INDEX])
    upload_latency = time() - start
    latencies["upload_data"] = upload_latency
    timestamps["finishing_time"] = time()

    print("Function completed!")    
    return jsonify({'statusCode': 200, "latencies": latencies, "timestamps": timestamps, "metadata": metadata})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))    