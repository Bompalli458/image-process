import uuid
import io
import logging
from PIL import Image  # Import Pillow library
from botocore.exceptions import ClientError  # Import specific Boto3 exception
from aws_config import s3_client
from config import BUCKET_NAME
import requests

logger = logging.getLogger(__name__)

def upload_image_to_s3(image_url):
    """
    Uploads a resized and compressed image to S3 from a given URL and returns the URL of the uploaded object.

    :param image_url: The URL of the image to upload.
    :return: The URL of the uploaded image or None on error.
    """
    try:
        # Download the image from the URL
        try:
            response = requests.get(image_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except requests.RequestException as e:
            logger.error('Failed to download image from URL: %s with exception: %s', image_url, str(e))
            return None

        # Open the image and get its dimensions
        try:
            image = Image.open(io.BytesIO(response.content))
            width, height = image.size
        except (IOError, SyntaxError) as e:
            logger.error('Failed to process image from URL: %s with exception: %s', image_url, str(e))
            return None

        # Calculate new dimensions for 50% size reduction
        new_width = int(width * 0.5)
        new_height = int(height * 0.5)

        # Resize the image
        resized_image = image.resize((new_width, new_height))

        # Convert resized image to JPEG format and compress to 50% quality
        converted_image = resized_image.convert('RGB')  # Convert to RGB format (adjust as needed)
        compressed_image_data = io.BytesIO()
        converted_image.save(compressed_image_data, format='JPEG', quality=50)

        # Upload the compressed image to S3
        s3_key = f"{uuid.uuid4()}.jpg"
        logger.info('Uploading compressed image to S3 with key: %s', s3_key)
        try:
            s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=compressed_image_data.getvalue(), ContentType='image/jpeg')
        except ClientError as e:
            logger.error('Failed to upload image to S3 with exception: %s', str(e))
            return None

        output_image_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
        logger.info('Image uploaded successfully. Output URL: %s', output_image_url)
        return output_image_url
    except Exception as e:
        logger.error('Unexpected error occurred: %s', str(e))
        return None  # Handle unexpected errors by returning None
