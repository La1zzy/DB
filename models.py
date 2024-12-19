from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, index=True)  # Added index
    birth_date = db.Column(db.Date)
    biography = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    books = db.relationship('Book', back_populates='author', cascade="all, delete")

class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)  # Added index
    founded_year = db.Column(db.Integer)
    location = db.Column(db.String(200))
    books = db.relationship('Book', back_populates='publisher', cascade="all, delete")

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, index=True)  # Already indexed
    isbn = db.Column(db.String(13), unique=True, nullable=True, index=True)  # Added index
    publication_date = db.Column(db.Date, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    description = db.Column(db.Text, nullable=True)
    page_count = db.Column(db.Integer, nullable=True)
    language = db.Column(db.String(20), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False, index=True)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'), nullable=False, index=True)
    
    __table_args__ = (
        db.Index('idx_author_publisher', 'author_id', 'publisher_id'),
    )
    
    author = db.relationship('Author', back_populates='books')
    publisher = db.relationship('Publisher', back_populates='books')