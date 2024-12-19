from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity,
    get_jwt,
    current_user
)
from datetime import datetime, timezone
from models import db, Author, Book, Publisher, User, TokenBlocklist

routes = Blueprint('routes', __name__)

# Аутентификация
@routes.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400
        
        user = User(username=data['username'])
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "User created successfully",
            "user_id": user.id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@routes.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return jsonify({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": user.id
            }), 200
        
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@routes.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token}), 200

@routes.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    
    token_block = TokenBlocklist(jti=jti, created_at=now)
    db.session.add(token_block)
    db.session.commit()
    
    return jsonify({"message": "Successfully logged out"}), 200

# Защищенные endpoints для Author
@routes.route('/authors', methods=['POST'])
@jwt_required()
def create_author():
    data = request.json
    author = Author(
        name=data['name'],
        email=data.get('email'),
        birth_date=datetime.strptime(data.get('birth_date'), '%Y-%m-%d').date() if data.get('birth_date') else None,
        biography=data.get('biography')
    )
    db.session.add(author)
    db.session.commit()
    return jsonify({
        "id": author.id,
        "name": author.name,
        "email": author.email,
        "birth_date": author.birth_date.isoformat() if author.birth_date else None,
        "biography": author.biography
    }), 201

@routes.route('/authors/<int:author_id>', methods=['GET'])
@jwt_required()
def get_author(author_id):
    author = Author.query.get_or_404(author_id)
    return jsonify({
        "id": author.id,
        "name": author.name,
        "email": author.email,
        "birth_date": author.birth_date.isoformat() if author.birth_date else None,
        "biography": author.biography
    })

@routes.route('/authors', methods=['GET'])
@jwt_required()
def get_authors():
    authors = Author.query.all()
    return jsonify([{"id": a.id, "name": a.name} for a in authors])

@routes.route('/authors/<int:author_id>', methods=['PUT'])
@jwt_required()
def update_author(author_id):
    data = request.json
    author = Author.query.get_or_404(author_id)
    author.name = data['name']
    db.session.commit()
    return jsonify({"id": author.id, "name": author.name})

@routes.route('/authors/<int:author_id>', methods=['DELETE'])
@jwt_required()
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    return '', 204


@routes.route('/publishers', methods=['POST'])
@jwt_required()
def create_publisher():
    data = request.json
    publisher = Publisher(
        name=data['name'],
        founded_year=data.get('founded_year'),
        location=data.get('location')
    )
    db.session.add(publisher)
    db.session.commit()
    return jsonify({
        "id": publisher.id,
        "name": publisher.name,
        "founded_year": publisher.founded_year,
        "location": publisher.location
    }), 201

@routes.route('/publishers/<int:publisher_id>', methods=['GET'])
@jwt_required()
def get_publisher(publisher_id):
    publisher = Publisher.query.get_or_404(publisher_id)
    return jsonify({"id": publisher.id, "name": publisher.name})

@routes.route('/publishers', methods=['GET'])
@jwt_required()
def get_publishers():
    publishers = Publisher.query.all()
    return jsonify([{"id": p.id, "name": p.name} for p in publishers])

@routes.route('/publishers/<int:publisher_id>', methods=['PUT'])
@jwt_required()
def update_publisher(publisher_id):
    data = request.json
    publisher = Publisher.query.get_or_404(publisher_id)
    publisher.name = data['name']
    db.session.commit()
    return jsonify({"id": publisher.id, "name": publisher.name})

@routes.route('/publishers/<int:publisher_id>', methods=['DELETE'])
@jwt_required()
def delete_publisher(publisher_id):
    publisher = Publisher.query.get_or_404(publisher_id)
    db.session.delete(publisher)
    db.session.commit()
    return '', 204


@routes.route('/books', methods=['POST'])
@jwt_required()
def create_book():
    data = request.json
    book = Book(title=data['title'], author_id=data['author_id'], publisher_id=data['publisher_id'])
    db.session.add(book)
    db.session.commit()
    return jsonify({"id": book.id, "title": book.title, "author_id": book.author_id, "publisher_id": book.publisher_id}), 201

@routes.route('/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify({"id": book.id, "title": book.title, "author_id": book.author_id, "publisher_id": book.publisher_id})

@routes.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    return jsonify([{"id": b.id, "title": b.title, "author_id": b.author_id, "publisher_id": b.publisher_id} for b in books])

@routes.route('/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    data = request.json
    book = Book.query.get_or_404(book_id)
    book.title = data['title']
    book.author_id = data['author_id']
    book.publisher_id = data['publisher_id']
    db.session.commit()
    return jsonify({"id": book.id, "title": book.title, "author_id": book.author_id, "publisher_id": book.publisher_id})

@routes.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return '', 204
