import boto3
import os
import sys
from time import time

import cv2

s3_client = boto3.client('s3')

TMP = "/tmp/"
FILE_NAME_INDEX = 0
FILE_PATH_INDEX = 2

def video_processing(file_name, video_path):
    result_file_path = '/tmp/'+file_name+'-output.avi'

    video = cv2.VideoCapture(video_path)

    width = int(video.get(3))
    height = int(video.get(4))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(result_file_path, fourcc, 20.0, (width, height))

    start = time()
    while(video.isOpened()):
        ret, frame = video.read()

        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            im = cv2.imwrite('/tmp/tmp.jpg', gray_frame)
            gray_frame = cv2.imread('/tmp/tmp.jpg')
            out.write(gray_frame)
        else:
            break

    latency = time() - start

    video.release()
    out.release()
    return latency, result_file_path

def lambda_handler(event, context):
    src_bucket = event['src_bucket']
    object_key = event['object_key']
    dst_bucket = event['dst_bucket']
    download_path = '/tmp/'+object_key

    s3_client.download_file(src_bucket, object_key, download_path)

    latency, upload_path = video_processing(object_key, download_path)

    s3_client.upload_file(upload_path, dst_bucket, upload_path.split("/")[FILE_PATH_INDEX])

    print latency
    return latency
