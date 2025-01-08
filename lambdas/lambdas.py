import boto3
import json

def get_movies(event, context):
    dynamodb = boto3.client('dynamodb')
    try:
        all_movies = []
        response = dynamodb.scan(TableName=event.get("db_name"))
        all_movies.extend(change_format(response.get('Items', [])))
        
        while 'LastEvaluatedKey' in response:
            response = dynamodb.scan(
                TableName=event.get("db_name"),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )

            all_movies.extend(change_format(response.get('Items', [])))
        
        return all_movies
    except Exception as e:
        print(f"Error fetching items: {e}")
        return []
    
def get_movies_by_year(event, context):
    dynamodb = boto3.client('dynamodb')
    try:
        all_movies = []
        response = dynamodb.scan(
            TableName=event.get("db_name"),
            FilterExpression="releaseYear = :year",
            ExpressionAttributeValues={":year": {"S": event.get("year")}}
        )
        all_movies.extend(change_format(response.get('Items', [])))
        
        while 'LastEvaluatedKey' in response:
            response = dynamodb.scan(
                TableName=event.get("db_name"),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            all_movies.extend(change_format(response.get('Items', [])))
        
        return all_movies
    except Exception as e:
        print(f"Error fetching items: {e}")
        return []
    
def generate_summary(event, context):
    bedrock = boto3.client('bedrock-runtime')

    prompt = f'Generate a concise summary for the movie {event.get("title")}.'

    response = bedrock.invoke_model(
        modelId="amazon.nova-micro-v1:0",
        contentType="application/json",
        accept= "application/json",
        body= json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        })
    )

    response_body = json.loads(response['body'].read().decode('utf-8'))['output']['message']['content'][0]['text']
    return response_body;

    
def change_format(items):
    return [
        {
            "title": item["title"]["S"],
            "releaseYear": item["releaseYear"]["S"],
            "genre": item["genre"]["S"],
            "coverUrl": item["coverUrl"]["S"]
        }
        for item in items
    ]