import os
import json
import psycopg2
import boto3
import fitz  # PyMuPDF
from botocore.exceptions import ClientError

# Initialize S3 client
s3 = boto3.client('s3')

# PostgreSQL connection details
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']

def extract_text_from_pdf(file_content):
    # Load PDF file
    pdf_document = fitz.open(stream=file_content, filetype="pdf")
    text = ""
    # Extract text from each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

def lambda_handler(event, context):
    try:
        # Parse the S3 event
        for record in event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']

            # Get the object from S3
            response = s3.get_object(Bucket=bucket_name, Key=object_key)
            file_content = response['Body'].read()

            # Determine the file type and extract content accordingly
            if object_key.endswith('.txt'):
                content = file_content.decode('utf-8')
            elif object_key.endswith('.pdf'):
                content = extract_text_from_pdf(file_content)
            else:
                # Unsupported file type
                continue

            # Establish PostgreSQL connection
            connection = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            cursor = connection.cursor()

            # Insert the document into the database
            cursor.execute("""
                INSERT INTO documents (filename, content, object_key)
                VALUES (%s, %s, %s)
                """, (object_key, content, object_key)
            )

            # Commit the transaction
            connection.commit()

            # Close the cursor and connection
            cursor.close()
            connection.close()

        return {
            'statusCode': 200,
            'body': json.dumps('Successfully processed S3 event')
        }

    except ClientError as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing S3 event: {str(e)}")
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal server error: {str(e)}")
        }
