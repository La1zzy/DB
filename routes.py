from flask import Blueprint, jsonify, request
from models import db, Author, Book, Publisher

routes = Blueprint('routes', __name__)

@routes.route('/authors', methods=['POST'])
def create_author():
    data = request.json
    author = Author(name=data['name'])
    db.session.add(author)
    db.session.commit()
    return jsonify({"id": author.id, "name": author.name}), 201

@routes.route('/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    author = Author.query.get_or_404(author_id)
    return jsonify({"id": author.id, "name": author.name})

@routes.route('/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify([{"id": a.id, "name": a.name} for a in authors])

@routes.route('/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    data = request.json
    author = Author.query.get_or_404(author_id)
    author.name = data['name']
    db.session.commit()
    return jsonify({"id": author.id, "name": author.name})

@routes.route('/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    return '', 204


@routes.route('/publishers', methods=['POST'])
def create_publisher():
    data = request.json
    publisher = Publisher(name=data['name'])
    db.session.add(publisher)
    db.session.commit()
    return jsonify({"id": publisher.id, "name": publisher.name}), 201

@routes.route('/publishers/<int:publisher_id>', methods=['GET'])
def get_publisher(publisher_id):
    publisher = Publisher.query.get_or_404(publisher_id)
    return jsonify({"id": publisher.id, "name": publisher.name})

@routes.route('/publishers', methods=['GET'])
def get_publishers():
    publishers = Publisher.query.all()
    return jsonify([{"id": p.id, "name": p.name} for p in publishers])

@routes.route('/publishers/<int:publisher_id>', methods=['PUT'])
def update_publisher(publisher_id):
    data = request.json
    publisher = Publisher.query.get_or_404(publisher_id)
    publisher.name = data['name']
    db.session.commit()
    return jsonify({"id": publisher.id, "name": publisher.name})

@routes.route('/publishers/<int:publisher_id>', methods=['DELETE'])
def delete_publisher(publisher_id):
    publisher = Publisher.query.get_or_404(publisher_id)
    db.session.delete(publisher)
    db.session.commit()
    return '', 204


@routes.route('/books', methods=['POST'])
def create_book():
    data = request.json
    book = Book(title=data['title'], author_id=data['author_id'], publisher_id=data['publisher_id'])
    db.session.add(book)
    db.session.commit()
    return jsonify({"id": book.id, "title": book.title, "author_id": book.author_id, "publisher_id": book.publisher_id}), 201

@routes.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify({"id": book.id, "title": book.title, "author_id": book.author_id, "publisher_id": book.publisher_id})

@routes.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{"id": b.id, "title": b.title, "author_id": b.author_id, "publisher_id": b.publisher_id} for b in books])

@routes.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    book = Book.query.get_or_404(book_id)
    book.title = data['title']
    book.author_id = data['author_id']
    book.publisher_id = data['publisher_id']
    db.session.commit()
    return jsonify({"id": book.id, "title": book.title, "author_id": book.author_id, "publisher_id": book.publisher_id})

@routes.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return '', 204
