from flask import Flask, jsonify, abort, request, make_response
from flask_mysqldb import MySQL

# Initialize the Flask application
app = Flask(__name__)

# Configure MySQL database connection
app.config['MYSQL_HOST'] = 'book-store-rds.c9cysu6e2wtc.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'kenny'
app.config['MYSQL_PASSWORD'] = '2INZKAGjuBPubaGHzTKK'
app.config['MYSQL_DB'] = 'bookstore_db'
app.config['MYSQL_PORT'] = 3306

# Initialize MySQL
mysql = MySQL(app)

# Initialize the bookstore database with a books table and sample data
def init_bookstore_db():
    with app.app_context():
        connection = mysql.connection
        cursor = connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS books;')
        cursor.execute("""
            CREATE TABLE books (
                book_id INT NOT NULL AUTO_INCREMENT,
                title VARCHAR(100) NOT NULL,
                author VARCHAR(100),
                is_sold BOOLEAN NOT NULL DEFAULT 0,
                PRIMARY KEY (book_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        cursor.execute("""
            INSERT INTO books (title, author, is_sold) VALUES
                ("The Midnight Library", "Matt Haig", 1),
                ("The Invisible Life of Addie LaRue", "V.E. Schwab", 0),
                ("The Silent Patient", "Alex Michaelides", 0),
                ("Project Hail Mary", "Andy Weir", 1),
                ("The Night Circus", "Erin Morgenstern", 0);
        """)
        connection.commit()

# Fetch all books from the database
def get_all_books():
    with app.app_context():
        connection = mysql.connection
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM books;")
        rows = cursor.fetchall()
        return [{'book_id': row[0], 'title': row[1], 'author': row[2], 'is_sold': bool(row[3])} for row in rows]

# Fetch a book by its ID
def find_book(book_id):
    with app.app_context():
        connection = mysql.connection
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM books WHERE book_id=%s;", (book_id,))
        row = cursor.fetchone()
        return {'book_id': row[0], 'title': row[1], 'author': row[2], 'is_sold': bool(row[3])} if row else None

# Add a new book to the database
def insert_book(title, author):
    with app.app_context():
        connection = mysql.connection
        cursor = connection.cursor()
        cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s);", (title, author))
        connection.commit()
        cursor.execute("SELECT * FROM books WHERE book_id=%s;", (cursor.lastrowid,))
        row = cursor.fetchone()
        return {'book_id': row[0], 'title': row[1], 'author': row[2], 'is_sold': bool(row[3])}

# Update an existing book's details
def change_book(book):
    with app.app_context():
        connection = mysql.connection
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE books
            SET title=%s, author=%s, is_sold=%s
            WHERE book_id=%s;
        """, (book['title'], book['author'], book['is_sold'], book['book_id']))
        connection.commit()
        cursor.execute("SELECT * FROM books WHERE book_id=%s;", (book['book_id'],))
        row = cursor.fetchone()
        return {'book_id': row[0], 'title': row[1], 'author': row[2], 'is_sold': bool(row[3])}

# Remove a book from the database
def remove_book(book_id):
    with app.app_context():
        connection = mysql.connection
        cursor = connection.cursor()
        cursor.execute("DELETE FROM books WHERE book_id=%s;", (book_id,))
        connection.commit()
        cursor.execute("SELECT * FROM books WHERE book_id=%s;", (book_id,))
        return cursor.fetchone() is None

@app.route('/')
def home():
    return """
        <html>
            <head>
                <title>Kenny's Bookstore API</title>
            </head>
            <body> 
                <h1>Welcome to Kenny's Bookstore API Service</h1>
                <img src="https://www.shutterstock.com/shutterstock/photos/415603990/display_1500/stock-vector-well-done-paper-banner-with-color-confetti-vector-illustration-415603990.jpg" alt="Well Done">
            </body>
        </html>
    """

@app.route('/books', methods=['GET'])
def get_books():
    return jsonify({'books': get_all_books()})

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = find_book(book_id)
    if book is None:
        abort(404)
    return jsonify({'book': book})

@app.route('/books', methods=['POST'])
def add_book():
    if not request.json or 'title' not in request.json:
        abort(400)
    new_book = insert_book(request.json['title'], request.json.get('author', ''))
    return jsonify({'new_book': new_book}), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = find_book(book_id)
    if book is None:
        abort(404)
    if not request.json:
        abort(400)
    updated_book = {
        'book_id': book_id,
        'title': request.json.get('title', book['title']),
        'author': request.json.get('author', book['author']),
        'is_sold': int(request.json.get('is_sold', book['is_sold']))
    }
    return jsonify({'updated_book': change_book(updated_book)})

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = find_book(book_id)
    if book is None:
        abort(404)
    return jsonify({'result': remove_book(book_id)})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

if __name__ == '__main__':
    with app.app_context():
        init_bookstore_db()
    app.run(host='0.0.0.0', port=80)
