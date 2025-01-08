import boto3

def get_movies():
    dynamodb = boto3.client('dynamodb')
    try:
        all_movies = []
        response = dynamodb.scan(TableName="serverless-movies-api-db")
        all_movies.extend(change_format(response.get('Items', [])))
        
        while 'LastEvaluatedKey' in response:
            response = dynamodb.scan(
                TableName="serverless-movies-api-db",
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

print(get_movies())