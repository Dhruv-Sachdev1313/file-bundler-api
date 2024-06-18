from app.services import db_services
from flask import request
from flask_restful import Resource
# from ..services.s3_service.py import S3Service
from app.services.s3_services import S3Service
from app.services.db_services import DBService
from zipfile import ZipFile
from io import BytesIO
from app.config import Config

class FileUploadResource(Resource):
    def post(self):
        if 'file' not in request.files:
            return {'message': 'No file part'}, 400
        file = request.files['file']
        if file.filename == '':
            return {'message': 'No selected file'}, 400
        if file and file.filename.endswith('.zip'):
            s3_service = S3Service()
            db_services = DBService()
            # make a temp directory and extract the zip file
            with ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall('/tmp')
            # upload the extracted files to S3   and add an entry to the database
            for extracted_file in zip_ref.namelist():
                with open(extracted_file, 'rb') as f:
                    obj_key = f"{file.filename}/{extracted_file}"
                    s3_service.upload_file(f, Config.S3_BUCKET, obj_key)
                    db_services.insert_document(extracted_file, f.read(), object_key=obj_key)
            return {'message': 'File uploaded successfully'}, 200
        else:
            return {'message': 'Invalid file type'}, 400
