from flask import abort

import json
import boto3
import random

class AwsUtils:
    def __init__(self):
        pass

    def build():
        return AwsUtils()

    def create_s3_bucket(self, bucket_name=None):

        s3 = boto3.client('s3')

        if bucket_name is None or bucket_name == '':
            bucket_name = f"serverless-movies-api-cover-images-{random.randint(10**4, 10**5 - 1)}"

        try:
            s3.create_bucket(
                Bucket=bucket_name
            )

            s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )

            bucket_policy = {
                "Id": "Policy1735924252388",
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Stmt1735924251093",
                        "Action": [
                            "s3:GetObject"
                        ],
                        "Effect": "Allow",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                        "Principal": "*"
                    }
                ]
            }

            s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )

            return bucket_name
        except Exception as e:
            return abort(400, str(e))

    def delete_s3_bucket(self, bucket_name):

        s3 = boto3.client('s3')

        try:
            s3.head_bucket(
                Bucket=bucket_name,
            )
        except Exception as e:
            abort(400, str(e))
        
        paginator = s3.get_paginator('list_objects_v2')

        pages = paginator.paginate(Bucket=bucket_name)

        objects_in_bucket = []

        for page in pages:
            if 'Contents' in page:
                objects_in_bucket = [{'Key': obj['Key']} for obj in page['Contents']]
                s3.delete_objects(Bucket=bucket_name, Delete={'Objects': objects_in_bucket})
        
        s3.delete_bucket(
            Bucket=bucket_name,
        )

        return 'bucket deleted successfully'
    
    def create_db(self, db_name=None):

        db = boto3.client('dynamodb')

        if db_name is None or db_name == '':
            db_name = "serverless-movies-api-db"

        try:
            db.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'title',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'releaseYear',
                        'AttributeType': 'S'
                    }
                ],
                TableName=db_name,
                KeySchema=[
                    {
                        'AttributeName': 'title',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'releaseYear',
                        'KeyType': 'RANGE'
                    }
                ],
                BillingMode='PROVISIONED',
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                },
            )
            return db_name
        except Exception as e:
            abort(400, str(e))
    
    def delete_db(self):

        db = boto3.client('dynamodb')

        try:
            db.delete_table(
                TableName=db_name
            )
        except Exception as e:
            abort(400, str(e))
