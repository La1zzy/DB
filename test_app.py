import time
import random
from app import create_app
from models import db, Author, Book, Publisher
import string

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return execution_time
    return wrapper

class DatabasePerformanceTest:
    def __init__(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
    def cleanup(self):
        db.session.query(Book).delete()
        db.session.query(Author).delete()
        db.session.query(Publisher).delete()
        db.session.commit()
        
    @measure_time
    def insert_test_data(self, count):
        # Вставка авторов
        authors = [Author(name=generate_random_string(10)) for _ in range(count // 100)]
        db.session.bulk_save_objects(authors)
        db.session.commit()
        
        # Вставка издателей
        publishers = [Publisher(name=generate_random_string(10)) for _ in range(count // 200)]
        db.session.bulk_save_objects(publishers)
        db.session.commit()
        
        # Получение ID авторов и издателей
        author_ids = [a.id for a in Author.query.all()]
        publisher_ids = [p.id for p in Publisher.query.all()]
        
        # Вставка книг
        books = [
            Book(
                title=generate_random_string(15),
                author_id=random.choice(author_ids),
                publisher_id=random.choice(publisher_ids)
            ) for _ in range(count)
        ]
        db.session.bulk_save_objects(books)
        db.session.commit()
        
    @measure_time
    def select_test(self):
        Book.query.all()
        
    @measure_time
    def update_test(self):
        # Обновляем все записи
        books = Book.query.all()
        for book in books:
            book.title = generate_random_string(15)
        db.session.commit()
        
    @measure_time
    def delete_test(self):
        # Удаляем все записи
        books = Book.query.all()
        for book in books:
            db.session.delete(book)
        db.session.commit()

def run_performance_tests():
    test = DatabasePerformanceTest()
    data_sizes = [1000, 10000, 100000, 1000000]
    results = []
    
    for size in data_sizes:
        print(f"\nТестирование для {size} записей:")
        test.cleanup()
        
        # Измерение времени вставки
        insert_time = test.insert_test_data(size)
        print(f"Время вставки: {insert_time:.2f} секунд")
        
        # Измерение времени выборки
        select_time = test.select_test()
        print(f"Время выборки: {select_time:.2f} секунд")
        
        # Измерение времени обновления
        update_time = test.update_test()
        print(f"Время обновления {size} записей: {update_time:.2f} секунд")
        
        # Измерение времени удаления
        delete_time = test.delete_test()
        print(f"Время удаления {size} записей: {delete_time:.2f} секунд")
        
        results.append({
            'size': size,
            'insert': insert_time,
            'select': select_time,
            'update': update_time,
            'delete': delete_time
        })
    
    return results

if __name__ == '__main__':
    results = run_performance_tests()
