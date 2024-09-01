import boto3
import os

# Retrieve AWS credentials from environment variables or use a default profile
ACCESS_KEY_ID = os.getenv('ACCESS_KEY_ID')
SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')  # Default region if not set

def create_s3_client():
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        return s3_client
    except Exception as e:
        print(f"Error creating S3 client: {e}")
        raise

s3_client = create_s3_client()
