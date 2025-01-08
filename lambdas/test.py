import boto3
import json

def generate_summary():
    bedrock = boto3.client('bedrock-runtime')

    prompt = f'Generate a concise summary for the movie inception.'

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

    return json.loads(response['body'].read().decode('utf-8'))['output']['message']['content'][0]['text']

print(generate_summary())