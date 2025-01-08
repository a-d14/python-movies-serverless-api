import boto3

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