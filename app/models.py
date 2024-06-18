from app import db
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import TSVECTOR

class Document(db.Model):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    object_key = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __ts_vector__ = db.Index(
        'documents_content_idx', 'to_tsvector(\'english\', content)', postgresql_using='gin'
    )
