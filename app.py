from flask import Flask, request, jsonify
from awsutils import AwsUtils

app = Flask(__name__)

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
    """

@app.route('/create-bucket', methods=['POST'])
def create_bucket():
    data = request.json

    try:
        return jsonify(
            {
                "bucket_name": AwsUtils.build().create_s3_bucket(data['bucket_name'])
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/delete-bucket', methods=['POST'])
def delete_bucket():
    data = request.json

    try:
        AwsUtils.build().delete_s3_bucket(data['bucket_name'])
        return jsonify(
            {
                "status": "Bucket deleted successfully"
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)