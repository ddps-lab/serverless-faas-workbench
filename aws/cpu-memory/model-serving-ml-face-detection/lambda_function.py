import boto3
import os
import sys
import uuid
from time import time
import cv2

s3_client = boto3.client('s3')

TMP = "/tmp/"
FILE_NAME_INDEX = 0
FILE_PATH_INDEX = 2

def video_processing(file_name, video_path):
    result_file_path = '/tmp/'+file_name+'-detection.avi'

    video = cv2.VideoCapture(video_path)

    width = int(video.get(3))
    height = int(video.get(4))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(result_file_path, fourcc, 20.0, (width, height))

    face_cascade = cv2.CascadeClassifier('/tmp/haarcascade_frontalface_default.xml')

    start = time()  
    while(video.isOpened()):
        ret, frame = video.read()

        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
            print "Found {0} faces!".format(len(faces))
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            out.write(frame)
        else:
            break

    latency = time() - start

    video.release()
    out.release()
    return latency, result_file_path

def lambda_handler(event, context):
    latency_list = []

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)

        s3_client.download_file("video-face-detection", "haarcascade_frontalface_default.xml", "/tmp/haarcascade_frontalface_default.xml")

        s3_client.download_file(bucket, key, download_path)
        file_name = key.split(".")[FILE_NAME_INDEX]

        latency, upload_path = video_processing(file_name, download_path)
        latency_list.append(latency)

        s3_client.upload_file(upload_path, 'result-video-processing', upload_path.split("/")[FILE_PATH_INDEX])
    print latency_list
    return latency_list

