# app.py
from flask import Flask, render_template, request, redirect, url_for, flash,session
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import secrets
from sqlalchemy import text
from sqlalchemy import and_


# Generate a secure key
secure_key = secrets.token_hex(32)

print("Secure Key:", secure_key)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = secure_key
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'











class User(UserMixin, db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

   
    
   
    
   
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Book(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    cover_image = db.Column(db.String(100))
    reading_status = db.Column(db.String(20))  # Added reading status field
    ratings = db.relationship('Rating', backref='book', lazy=True)
    reviews = db.relationship('Review', backref='book', lazy=True)
   

# Association Table (Many-to-Many)

class UserBooks(db.Model):
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key = True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key = True)
    


    
    



    





class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)


# Enclose db.create_all() in an application context
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"An error occurred: {e}")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully signed up!')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            
            user_string = str(user)
            user_id = int(user_string.split()[1][:-1])
            #print(user_id)
            
            session['user_id'] = user_id
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login unsuccessful. Please check your username and password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        # Now you have the user_id, you can proceed with your logic
       
    else:
        return redirect(url_for('login'))
    
    try:

        '''sql_query = text ('SELECT Book.title, Book.author,Book.genre, Book.cover_image, Book.reading_status FROM Book JOIN UserBooks JOIN User ON UserBooks.user_id = User.id AND UserBooks.book_id ')
        books = db.session.execute(sql_query).fetchall()'''

        books = db.session.query(Book).join(UserBooks).join(User).filter(User.id == user_id).all()
        # If no books found, return an empty list
        if not books:
            books = []

    except:
        books = []

    
   
    #books = db.session.query(Book).join(UserBooks).filter(UserBooks.user_id == user_id).all()
    #books = db.session.query(Book)

    return render_template('index.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if 'user_id' in session:
        user_id = session['user_id']
        # Now you have the user_id, you can proceed with your logic
       
    else:
        return redirect(url_for('login'))
   
    
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        cover_image = request.form['cover_image']  # Assuming cover image URL is provided
        reading_status = request.form['reading_status']
        book = Book(title=title, author=author, genre=genre, cover_image=cover_image, reading_status=reading_status)
        db.session.add(book)
        db.session.commit()
        user_book_entry = UserBooks(user_id=user_id, book_id=book.id)
        db.session.add(user_book_entry)
        
        
        #user.books.append(book)
        
        db.session.commit()
        flash('Book added successfully!')
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.genre = request.form['genre']
        book.cover_image = request.form['cover_image']
        book.reading_status = request.form['reading_status']
        db.session.commit()
        flash('Book updated successfully!')
        return redirect(url_for('index'))
    return render_template('edit_book.html', book=book)

@app.route('/delete_book/<int:id>', methods=['POST'])
@login_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!')
    return redirect(url_for('index'))

@app.route('/book_details/<int:id>')
@login_required
def book_details(id):
    book = Book.query.get_or_404(id)
    # Calculate average rating for the book
    # Calculate_average_rating(book)
    # Check if the book object has an id attribute
    # Check if bookmark exists for the book
    
    if not hasattr(book, 'id'):
        # Handle the case where the book object does not have an id attribute
        # This could occur if the book object is None or if it is missing the id attribute for some reason
        # You might want to return an error message or redirect the user to a different page
        flash('Error: Book not found')
        return redirect(url_for('index'))  # Redirect to the homepage or another appropriate page
    
    # Continue with rendering the book details template
    return render_template('book_details.html', book=book)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    query = request.form['query']
    books = Book.query.filter(
        (Book.title.contains(query)) | 
        (Book.author.contains(query)) |
        (Book.genre.contains(query))
    ).all()
    return render_template('index.html', books=books)


@app.route('/rate_book/<int:id>', methods=['GET', 'POST'])
@login_required
def rate_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        rating_value = int(request.form['rating'])
        review_content = request.form['review']

        # Calculate average rating
        total_ratings = sum(rating.value for rating in book.ratings)
        num_ratings = len(book.ratings)
        if num_ratings > 0:
            average_rating = total_ratings / num_ratings
        else:
            average_rating = 0

        # Save rating
        rating = Rating(value=rating_value, book_id=id)
        db.session.add(rating)

        # Save review
        review = Review(content=review_content, book_id=id)
        db.session.add(review)

        db.session.commit()
        flash('Rating and review submitted successfully!')

        return redirect(url_for('book_details', id=id))
    return render_template('rate_book.html', book=book)

# Calculate average rating for each book
def calculate_average_rating(book):
    total_ratings = sum(rating.value for rating in book.ratings)
    num_ratings = len(book.ratings)
    if num_ratings > 0:
        book.average_rating = total_ratings / num_ratings
    else:
        book.average_rating = 0



@app.route('/add_bookmark/<int:id>', methods=['POST'])
@login_required
def add_bookmark(id):
    # Logic to add bookmark
    flash('Bookmark added successfully!')
    return redirect(url_for('book_details', id=id))



if __name__ == '__main__':
    app.run(debug=True)










