from flask import current_app
from app.models import Document
from app import db

class DBService:
    def insert_document(self, filename, content, object_key):
        try:
            document = Document(filename=filename, content=content, object_key=object_key)
            db.session.add(document)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Error inserting document: {e}")
            db.session.rollback()
            raise

    def search_documents(self, keyword):
        try:
            results = Document.query.filter(Document.content.match(keyword)).all()
            return [doc.filename for doc in results]
        except Exception as e:
            current_app.logger.error(f"Error searching documents: {e}")
            raise
