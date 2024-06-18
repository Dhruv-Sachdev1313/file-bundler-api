from flask import request
from flask_restful import Resource
from ..services.db_services import DBService

class SearchResource(Resource):
    def get(self):
        keyword = request.args.get('q')
        if not keyword:
            return {'message': 'Keyword is required'}, 400
        db_service = DBService()
        results = db_service.search_documents(keyword)
        return {'documents': results}, 200

class TextSearchResource(Resource):
    def post(self):
        data = request.json
        text = data.get('text')
        if not text:
            return {'message': 'Text is required'}, 400
        db_service = DBService()
        results = db_service.search_documents(text)
        return {'documents': results}, 200
