import boto3

def get_movies(table_name, year):
    dynamodb = boto3.client('dynamodb')
    try:
        all_movies = []
        response = dynamodb.scan(
            TableName=table_name,
            FilterExpression = f'releaseYear={year}'
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
