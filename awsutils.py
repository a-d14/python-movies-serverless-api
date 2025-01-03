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

    def delete_s3_bucket(self):

        s3 = boto3.client('s3')

        s3.delete_bucket(
            Bucket=self.bucket_name,
            ExpectedBucketOwner='string'
        )
        return 'bucket deleted successfully'
    

