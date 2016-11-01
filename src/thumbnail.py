from __future__ import print_function
import boto3
import os
import sys
import uuid
from PIL import Image, ImageOps
from os import path
     
s3_client = boto3.client('s3')
     
size_resized = (1280, 1280)
size_thumbnail = (256, 256)

def rename(path, size):
    tokens = path.split('/')
    name = '/'.join(tokens[:-1]) + "/" + "x".join([str(x) for x in size]) + "_" + tokens[-1]
    return name

def thumbnail(path, size, save_path):
    with Image.open(path) as image:
        isize = image.size
        if isize[0] > size[0] or isize[1] > size[1]:
            thumb = ImageOps.fit(image, size, Image.ANTIALIAS)
            thumb.save(save_path)


def resize(path, size,save_path):
    with Image.open(path) as image:
        isize = image.size
        if isize[0] > size[0] or isize[1] > size[1]:
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(save_path)

def generate_key(key, infix):
    return key.replace('original', infix)
     
def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key'] 
        s_key = key.replace('/','_')
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), s_key)
        s3_client.download_file(bucket, key, download_path)

        # thumbnail
        upload_path = '/tmp/thumbnail_{}_{}'.format(uuid.uuid4(),s_key)        
        resize(download_path, size_thumbnail, upload_path)
        s3_client.upload_file(upload_path, bucket, generate_key(key,'thumbnail'))

        # resize       
        upload_path = '/tmp/resized_{}_{}'.format(uuid.uuid4(),s_key)        
        resize(download_path, size_resized, upload_path)
        s3_client.upload_file(upload_path, bucket, generate_key(key,'resize'))


       
