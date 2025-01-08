import json

from flask import Flask, request, jsonify
from awsutils import AwsUtils

app = Flask(__name__)

awsutils = AwsUtils()

@app.route('/')
def home():
    return """
    Welcome. Here are the actions available to you.
    
    1.  POST /create-bucket
        Description: create an S3 bucket to store all movie posters
        Payload : {
            "bucket_name" : "string" (OPTIONAL) (DEFAULT - serverless-movies-api-cover-images-<randomly generated number>)
        }

    2. POST /delete-bucket
       Description: create an S3 bucket to store all movie posters
       Payload : {
            "bucket_name" : "string" (REQUIRED)
       }

    3. POST /create-db
       Description: create a DynamoDB table to store movies data.
       Payload : {
            "bucket_name" : "string" (OPTIONAL) (DEFAULT - serverless-movies-api-db)
       }
       
    4. POST /delete-db
       Description: delete a DynamoDB table.
       Payload : {
            "bucket_name" : "string" (REQUIRED)
       }
    """

@app.route('/create-bucket', methods=['POST'])
def create_bucket():
    data = request.json

    try:
        return jsonify(
            {
                "bucket_name": awsutils.create_s3_bucket(data['bucket_name']),
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/delete-bucket', methods=['POST'])
def delete_bucket():
    data = request.json

    try:
        awsutils.delete_s3_bucket(data['bucket_name'])
        return jsonify(
            {
                "status": "Bucket deleted successfully"
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/create-db', methods=['POST'])
def create_db():
    data = request.json
    try:
        return jsonify(
            {
                "arn": awsutils.create_db(data['db_name'])
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/delete-db', methods=['POST'])
def delete_db():
    data = request.json

    try:
        awsutils.delete_db(data['db_name'])
        return jsonify(
            {
                "status": "DB deleted successfully"
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/insert-items', methods=['POST'])
def insert_items_db():
    data = request.json

    db_name = request.args.get('tableName', default='serverless-movies-api-db')
    
    bucket_name = request.args.get('bucketName')

    print(bucket_name)

    if bucket_name is None or bucket_name == '':
        return jsonify({"error": "bucket name must be provided"}), 400


    try:
        awsutils.insert_items_db(db_name, bucket_name, data)
        return jsonify(
            {
                "status": "Items inserted succesfully"
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/create-policy', methods=['POST'])
def create_policy():
    data = request.json
    try:
        response = awsutils.create_policy(data['policy-name'], data['policy-document'])

        return jsonify(
            {
                "arn": f"{response}"
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400    
    
@app.route('/create-role', methods=['POST'])
def create_role():
    data = request.json

    try:
        response = awsutils.create_role(data['arn'], data['role-name'], data['assume-role-policy'])

        return jsonify(
                {
                    "arn": f"{response}"
                }
            ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400    

@app.route('/create-lambda', methods=['POST'])
def create_lambda():
    data = request.json
    try:
        response = awsutils.create_lambda(data['name'], data['file-path'], data['role-arn'])

        return jsonify(
                {
                    "name": f"{response}"
                }
            ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400    
    
@app.route('/getmovies', methods=['GET'])
def get_movies():
    try:
        response = awsutils.get_movies()

        return jsonify(
            {
                "data": json.loads(response.read().decode('utf-8'))
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404
    
@app.route('/getmoviesbyyear/<year>', methods=['GET'])
def get_movies_by_year(year):
    try:
        response = awsutils.get_movies_by_year(year)

        return jsonify(
            {
                "data": json.loads(response.read().decode('utf-8'))
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/getmoviesummary/<title>', methods=['GET'])
def generate_movie_summary(title):
    try:
        response = awsutils.generate_movie_summary(title)

        response_payload = json.loads(response.read().decode('utf-8'))

        return jsonify(
            {
                "summary": response_payload
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    app.run(debug=True)