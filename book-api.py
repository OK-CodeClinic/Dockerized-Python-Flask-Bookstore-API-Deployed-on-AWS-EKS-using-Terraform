from flask import Flask, jsonify, abort, request, make_response
from flaskext.mysql import MySQL

# Initialize the Flask application
app = Flask(__name__)

# Configure MySQL database connection
app.config['MYSQL_DATABASE_HOST'] = 'flask-app-rds-db.c9cysu6e2wtc.us-east-1.rds.amazonaws.com'
app.config['MYSQL_DATABASE_USER'] = 'kenny'
app.config['MYSQL_DATABASE_PASSWORD'] = 'WjJA86Rh72nKSEU0HpRX'
app.config['MYSQL_DATABASE_DB'] = 'bookstore_db'
app.config['MYSQL_DATABASE_PORT'] = 3306

# Initialize MySQL
mysql = MySQL()
mysql.init_app(app)

# Initialize the bookstore database with a books table and sample data
def init_bookstore_db():
    with app.app_context():
        connection = mysql.connect()
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

# Fetch all books from the database
def get_all_books():
    with app.app_context():
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM books;")
        rows = cursor.fetchall()
        return [{'book_id': row[0], 'title': row[1], 'author': row[2], 'is_sold': bool(row[3])} for row in rows]

# Fetch a book by its ID
def find_book(book_id):
    with app.app_context():
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM books WHERE book_id=%s;", (book_id,))
        row = cursor.fetchone()
        return {'book_id': row[0], 'title': row[1], 'author': row[2], 'is_sold': bool(row[3])} if row else None

# Add a new book to the database
def insert_book(title, author):
    with app.app_context():
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s);", (title, author))
        cursor.execute("SELECT * FROM books WHERE book_id=%s;", (cursor.lastrowid,))
        row = cursor.fetchone()
        return {'book_id': row[0], 'title': row[1], 'author': row[2], 'is_sold': bool(row[3])}

# Update an existing book's details
def change_book(book):
    with app.app_context():
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE books
            SET title=%s, author=%s, is_sold=%s
            WHERE book_id=%s;
        """, (book['title'], book['author'], book['is_sold'], book['book_id']))
        cursor.execute("SELECT * FROM books WHERE book_id=%s;", (book['book_id'],))
        row = cursor.fetchone()
        return {'book_id': row[0], 'title': row[1], 'author': row[2], 'is_sold': bool(row[3])}

# Remove a book from the database
def remove_book(book_id):
    with app.app_context():
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM books WHERE book_id=%s;", (book_id,))
        cursor.execute("SELECT * FROM books WHERE book_id=%s;", (book_id,))
        return cursor.fetchone() is None

# Routes and error handling remain the same as in your original code

if __name__ == '__main__':
    with app.app_context():
        init_bookstore_db()
    app.run(host='0.0.0.0', port=80)
