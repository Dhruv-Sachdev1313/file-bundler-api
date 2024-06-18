from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from app.config import Config  # Absolute import

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.resources.file_upload import FileUploadResource  # Absolute import
    from app.resources.search import SearchResource, TextSearchResource  # Absolute import

    api = Api(app)
    api.add_resource(FileUploadResource, '/upload')
    api.add_resource(SearchResource, '/search')
    api.add_resource(TextSearchResource, '/text-search')

    with app.app_context():
        db.create_all()

    return app
