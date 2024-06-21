import boto3
from flask import current_app
from app import Config

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3', 
            region_name=Config.AWS_REGION, 
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID, 
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )

    def upload_file(self, file, bucket_name, object_name):
        try:
            self.s3_client.upload_fileobj(file, bucket_name, object_name)
        except Exception as e:
            current_app.logger.error(f"Error uploading file: {e}")
            raise

    def delete_file(self, bucket_name, object_name):
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        except Exception as e:
            current_app.logger.error(f"Error deleting file: {e}")
            raise

    def get_presigned_url(self, bucket_name, object_name):
        try:
            response = self.s3_client.generate_presigned_url('get_object', Params={'Bucket': Config.FINAL_BUCKET, 'Key': object_name})
            return response
        except Exception as e:
            current_app.logger.error(f"Error generating presigned URL: {e}")
            raise
