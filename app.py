from flask import Flask
from models import db, Author, Book, Publisher
from routes import routes
from config import Config
from datetime import datetime, date
import time
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    if isinstance(config_class, str):
        app.config.from_object(config_class)
    else:
        app.config.from_object(config_class)
    db.init_app(app)
    app.register_blueprint(routes)
    return app

def initialize_related_tables(n):
    """Инициализация таблиц author и publisher."""
    try:
        # Создаем авторов (1/100 от количества книг)
        authors = [
            Author(
                name=f"Author {i}",
                email=f"author{i}@example.com",
                birth_date=date(1950 + i % 50, 1 + i % 12, 1 + i % 28),
                biography=f"Biography of author {i}"
            )
            for i in range(n // 100)
        ]
        db.session.bulk_save_objects(authors)
        db.session.commit()
        
        # Создаем издателей (1/200 от количества книг)
        publishers = [
            Publisher(
                name=f"Publisher {i}",
                founded_year=1900 + i % 100,
                location=f"City {i}"
            )
            for i in range(n // 200)
        ]
        db.session.bulk_save_objects(publishers)
        db.session.commit()
        
        return True
    except Exception as e:
        logger.error(f"Error initializing related tables: {str(e)}")
        db.session.rollback()
        return False

def measure_query_performance(n):
    """Измерение производительности запросов."""
    try:
        author_ids = [author.id for author in Author.query.all()]
        publisher_ids = [publisher.id for publisher in Publisher.query.all()]
        
        # TEST INSERT
        start_time = time.time()
        books = []
        for i in range(n):
            book = Book(
                title=f"Book {i}",
                isbn=f"{i:013d}",
                publication_date=date(2000 + i % 23, 1 + i % 12, 1 + i % 28),
                price=round(random.uniform(9.99, 99.99), 2),
                description=f"Description for book {i}",
                page_count=random.randint(100, 1000),
                language=random.choice(['en', 'ru', 'fr', 'de']),
                author_id=random.choice(author_ids),
                publisher_id=random.choice(publisher_ids)
            )
            books.append(book)
            
            # Сохраняем партиями по 1000 записей
            if len(books) >= 1000:
                db.session.bulk_save_objects(books)
                db.session.commit()
                books = []
        
        if books:  # Сохраняем оставшиеся книги
            db.session.bulk_save_objects(books)
            db.session.commit()
        
        insert_time = time.time() - start_time
        logger.info(f"INSERT {n} records: {insert_time:.2f} seconds ({n/insert_time:.2f} records/sec)")
        
        # TEST SELECT
        start_time = time.time()
        books = Book.query.join(Author).join(Publisher).filter(
            Book.price > 20
        ).limit(1000).all()
        select_time = time.time() - start_time
        logger.info(f"SELECT with joins: {select_time:.2f} seconds")
        
        # TEST UPDATE
        start_time = time.time()
        books = Book.query.limit(1000).all()
        for book in books:
            book.price = round(random.uniform(9.99, 99.99), 2)
            book.page_count = random.randint(100, 1000)
        db.session.commit()
        update_time = time.time() - start_time
        logger.info(f"UPDATE 1000 records: {update_time:.2f} seconds ({1000/update_time:.2f} records/sec)")
        
        # TEST DELETE
        start_time = time.time()
        # Получаем ID первых 1000 книг
        book_ids = [book.id for book in Book.query.limit(1000).all()]
        # Удаляем книги по полученным ID
        Book.query.filter(Book.id.in_(book_ids)).delete(synchronize_session=False)
        db.session.commit()
        delete_time = time.time() - start_time
        logger.info(f"DELETE 1000 records: {delete_time:.2f} seconds ({1000/delete_time:.2f} records/sec)")
        
        return True
    except Exception as e:
        logger.error(f"Error during performance measurement: {str(e)}")
        db.session.rollback()
        return False

def run_performance_tests():
    """Запуск всех тестов производительности."""
    app = create_app()
    
    with app.app_context():
        # Создаем таблицы если их нет
        db.create_all()
        
        # Тестируем разные объемы данных
        for n in [1000, 10000, 100000, 1000000]:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing with {n} records...")
            logger.info('='*50)
            
            try:
                # Очищаем базу перед каждым тестом
                Book.query.delete()
                Author.query.delete()
                Publisher.query.delete()
                db.session.commit()
                
                # Инициализируем связанные таблицы
                if initialize_related_tables(n):
                    # Запускаем тесты производительности
                    measure_query_performance(n)
                else:
                    logger.error(f"Failed to initialize related tables for {n} records test")
            
            except Exception as e:
                logger.error(f"Error during test with {n} records: {str(e)}")
            
            finally:
                # Очищаем базу после теста
                Book.query.delete()
                Author.query.delete()
                Publisher.query.delete()
                db.session.commit()
                logger.info(f"Database cleaned up after {n} records test")

if __name__ == '__main__':
    run_performance_tests()
