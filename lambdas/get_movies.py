import boto3

def get_movies(event, context):
    dynamodb = boto3.client('dynamodb')
    try:
        all_movies = []
        response = dynamodb.scan(TableName=event.get("table_name"))
        all_movies.extend(response.get('Items', []))
        
        while 'LastEvaluatedKey' in response:
            response = dynamodb.scan(
                TableName=event.get("table_name"),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            all_movies.extend(response.get('Items', []))
        
        return all_movies
    except Exception as e:
        print(f"Error fetching items: {e}")
        return []