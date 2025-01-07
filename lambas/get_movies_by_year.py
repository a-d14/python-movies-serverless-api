import boto3

def get_movies_by_year(table_name, year):
    dynamodb = boto3.client('dynamodb')
    try:
        all_movies = []
        response = dynamodb.scan(
            TableName=table_name,
            FilterExpression="releaseYear = :year",
            ExpressionAttributeValues={":year": {"S": year}}
        )
        all_movies.extend(response.get('Items', []))
        
        while 'LastEvaluatedKey' in response:
            response = dynamodb.scan(
                TableName=table_name,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            all_movies.extend(response.get('Items', []))
        
        return all_movies
    except Exception as e:
        print(f"Error fetching items: {e}")
        return []

print(get_movies_by_year('serverless-movies-api-db', "2001"))