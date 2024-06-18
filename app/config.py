import os

class Config:
    AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
    S3_BUCKET = os.getenv('S3_BUCKET', 'your-s3-bucket-name')
    FINAL_BUCKET = os.getenv('FINAL_BUCKET', 'your-final-bucket-name')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:password@db:5432/mydatabase')
