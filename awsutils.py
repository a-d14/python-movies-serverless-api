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
        
    def __put_s3(self, bucket_name, file_path, file_name):
        s3 = boto3.client('s3')
        print('here')
        s3.put_object(
            Body=open(file_path, 'rb'),
            Bucket=bucket_name,
            Key=file_name,
            ContentType="image/jpeg"
        )
        return f"https://{bucket_name}.s3.us-east-1.amazonaws.com/{file_name}"


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

        self.db_name = db_name

        if db_name is None or db_name == '':
            db_name = "serverless-movies-api-db"

        try:
            response = db.create_table(
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

            table_arn = response['TableDescription']['TableArn']
            return table_arn
        except Exception as e:
            abort(400, str(e))

    def insert_items_db(self, db_name, bucket_name, items):
        db = boto3.client('dynamodb')

        for item in items:
            item['coverUrl'] = self.__put_s3(bucket_name, item['coverUrl'], item['title'])

        transformed_items = []
        for item in items:
            transformed_items.append({
                'PutRequest': {
                    'Item': {
                        'title': {'S': item['title']},
                        'releaseYear': {'S': item['releaseYear']},
                        'genre': {'S': item['genre']},
                        'coverUrl': {'S': item['coverUrl']}
                    }
                }
            })


        try:
            db.batch_write_item(
                RequestItems={
                    db_name: transformed_items
                }
            )
        except Exception as e:
            abort(400, str(e))

    
    def delete_db(self, db_name):

        db = boto3.client('dynamodb')

        try:
            db.delete_table(
                TableName=db_name
            )
        except Exception as e:
            abort(400, str(e))

    def create_role(self, role_name, policy_document):
        iam = boto3.client('iam')
        try:
            policy_response = iam.create_policy(
                PolicyName='DynamoReadAccess',
                PolicyDocument=json.dumps(policy_document)
            )

            role_response = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole"
                        }
                    ]
                    }
                )
            )

            iam.attach_role_policy(
                RoleName=role_response['Role']['RoleName'],
                PolicyArn=policy_response['Policy']['Arn']
            )

            return role_response['Role']['Arn']
        except Exception as e:
            abort(400, str(e))

    def create_lambda(self, func_name, func_path, role_arn):
        lf = boto3.client('lambda')

        with open(func_path, 'rb') as zip_file:
            zip_content = zip_file.read()

        try:
            lf.create_function(
                FunctionName=func_name,
                Runtime='python3.9',
                Handler=f'lambdas.{func_name}',
                Role=role_arn,
                Code={
                    'ZipFile': zip_content
                },
                Description='a function to retrieve all movies from movies DynamoDB database'
            )

            return func_name
        except Exception as e:
            abort(400, str(e))

    def get_movies(self):
        lf = boto3.client('lambda')
        try:
            response = lf.invoke(
                FunctionName='get_movies',
                Payload=json.dumps({
                    "db_name" : self.db_name if hasattr(self, 'db_name') and self.db_name else 'serverless-movies-api-db'
                })
            )

            return response['Payload']
        except Exception as e:
            abort(400, str(e))

    def get_movies_by_year(self, year):
        lf = boto3.client('lambda')
        try:
            response = lf.invoke(
                FunctionName='get_movies_by_year',
                Payload=json.dumps({
                    "db_name" : self.db_name if hasattr(self, 'db_name') and self.db_name else 'serverless-movies-api-db',
                    "year": year
                })
            )
            return response['Payload']
        except Exception as e:
            abort(400, str(e))