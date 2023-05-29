import boto3
import logging
from moto import mock_s3
from common import config

# Configure logging
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageWrapper:
    """
    A wrapper for a S3 bucket based storage for resulting files.
    """
    @mock_s3
    def __init__(self):
        self.client = boto3.client("s3")
        self.client.create_bucket(Bucket=config.S3_BUCKET_NAME)

    @mock_s3
    def upload_html_file(
        self,
        content,
        task_hash,
    ):
        """
        :param content: the content of the extracted HTML file.
        :param task_hash: the unique hash of each crawl request.
        :return: A public url for the stored file.
        """
        # Check if the bucket already exists
        logger.info('Checking if bucket exists')
        response = self.client.list_buckets()
        existing_buckets = [bucket['Name'] for bucket in response['Buckets']]
        if config.S3_BUCKET_NAME not in existing_buckets:
            logger.info('Creating bucket')
            # Create the bucket
            self.client.create_bucket(Bucket=config.S3_BUCKET_NAME)

        # Upload the file to the bucket
        logger.info('Storing result in bucket')
        s3_client = boto3.client('s3')
        try:
            s3_client.put_object(Bucket=config.S3_BUCKET_NAME, Key=task_hash, Body=content)
            logger.info('Generating URL')
            # Generate a public URL for the file
            url = self.client.generate_presigned_url(
                'get_object', Params={'Bucket': config.S3_BUCKET_NAME, 'Key': task_hash}, ExpiresIn=3600
            )
            return url
        except Exception as e:
            # Handle the exception or log the error message
            logger.info(f"An error occurred while uploading the HTML file: {str(e)}")
            return None

