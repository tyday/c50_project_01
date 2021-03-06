import os
import config

# import functools
from flask import Flask, session, redirect, escape, url_for, request, render_template, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
app.debug = True
# Check for environment variable
# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    # return "Project 1: TODO"
    if 'username' in session:
        user=session['username']
    else:
        user=None
    return render_template('index.html', user=user)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the username fro the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))
@app.route('/login/auth', methods = ['GET', 'POST'])
def login_auth():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        selection = db.execute(
            'SELECT * FROM users WHERE username=:param', ({"param":username})).fetchone() 
        password_check = check_password_hash(selection.password, password)
        if password_check is False:
            error = 'password is incorrect'
        
        if error is None and password_check is True:
            session['username'] = username
            session['user_id'] = selection.id
            return redirect(url_for('index'))
        print('line before flash', error)
        flash(error)

    # flights = db.execute('SELECT * FROM flights WHERE id=4')
    # retValue = ""
    # for flight in flights:
    #     retValue += flight.origin
    return render_template('login.html', error = error)
@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/register/auth', methods = ['GET','POST'])
def register_auth():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif db.execute(
            'SELECT * FROM users WHERE username=:param', ({"param":username})
        ).fetchone() is not None:
            error = 'User {} is already registered'.format(username)
        
        if error is None:
            db.execute(
                'INSERT INTO users (username, password, role) VALUES (:param1, :param2, :param3)',
                {"param1":username, "param2":generate_password_hash(password), "param3":'writer'}
            )
            # db.execute(users.insert(),{"username":username,"password":password})
            db.commit()
            return redirect(url_for('login'))
        flash(error)
    return render_template('register.html', error = error)

# Search results will be split up
# /search/results will be for more than one book found.
# may limit it to top ten or something
# /search/isdn will be for individual books

@app.route('/search/results', methods = ['GET','POST'])
def search_results():
    if request.method == 'POST' or request.method == 'GET':
        if 'username' in session:
            user=session['username']
        error = None
        search_type = None
        search_term = request.form['search_term']
        search_type = request.form['search_type']
        search_term = "%" + search_term + "%"
        if search_type == 'title':
            results = db.execute(
                "SELECT * FROM books WHERE title iLIKE :param2 LIMIT 10",
                ({"param1": search_type, "param2":search_term})
            )
        elif search_type == 'author':
            results = db.execute(
                "SELECT * FROM books WHERE author iLIKE :param2 LIMIT 10",
                ({"param1": search_type, "param2":search_term})
            )
        # elif search_type == 'isbn':
        #     results = db.execute(
        #         "SELECT * FROM books WHERE isbn iLIKE :param2 LIMIT 10",
        #         ({"param1": search_type, "param2":search_term})
        #     )
        else:
            results = db.execute(
                "SELECT * FROM books WHERE isbn iLIKE :param2 LIMIT 10",
                ({"param1": search_type, "param2":search_term})
            )
        resultstring ="Found no results"
        book_list = []
        for row in results:
            book_list.append(row)
        if len(book_list) == 0:
            resultstring = "Found no results"
        elif len(book_list) == 1:
            return redirect(url_for('show_book', isbn = book_list[0][0]))
            # resultstring = str(book_list[0])
        else:
            return render_template('show_book_multi.html', user=user, books=book_list)
            resultstring = str(book_list)
        return resultstring

@app.route('/book/<isbn>')
def show_book(isbn):
    result = db.execute(
        "SELECT * FROM books WHERE isbn=:param1",
        ({"param1":isbn})
    )
    reviews = db.execute(
        "SELECT * " #reviews.score, reviews.review, users.username
        "FROM reviews "
        "INNER JOIN books ON reviews.isbn = books.isbn "
        "INNER JOIN users ON reviews.user_id = users.id "
        "WHERE reviews.isbn=:param1",
        ({"param1":isbn})
    )
    print(reviews)
    ret_reviews = []
    # for review in reviews:
    #     print(str(review))
    #     ret_reviews.append({"score":review.score,"review":review.review})
    # print(review.username,session['username'])
    review_count = 0
    score_total = 0
    user_review = None
    if 'username' in session:
        user=session['username']
        for review in reviews:
            if review.username == session['username']:
                user_review = {"score":review.score, "review":review.review, "review_id": review.review_id,"user_id":review.user_id,"isbn":review.isbn}
                print(user_review)
                review_count += 1
                score_total += review.score
                print(user_review)
            else:
                # user_review = {"score":review.score, "review":review.review, "review_id": review.review_id,"user_id":review.user_id,"isbn":review.isbn}
                # print(user_review)
                score_total+= review.score
                review_count += 1
                ret_reviews.append({"score":review.score,"review":review.review, "reviewer":review.username})
    else:
        user=None
    # print(f'Total reviews {review_count}, Average score: {score_total/review_count}')
    # return render_template('index.html', user=user)
    row = result.fetchone()
    if row is None:
        return 'nothing here'
    else:
        book = {"title":row.title,"author":row.author,"isbn":row.isbn,"year":row.year}
        if review_count > 0:
            ret_scores = {"count":review_count,"average":(score_total/review_count)}
            reviews_list = {"user_review":user_review,"all_reviews":ret_reviews}
        else:
            ret_scores = None
            reviews_list = None
        return render_template('show_book.html', user=user, user_id = session['user_id'], book=book, reviews=reviews_list,scores=ret_scores)
    # if row is not "":
    #     return 'found book'
    # else: return 'didnt find book'

@app.route('/update_review', methods = ['GET','POST'])
def update_review():
    if request.method == 'POST':        
        db.execute(
            "UPDATE reviews set score = :param1, review = :param2 "
            "WHERE review_id = :param3",
            ({"param1":request.form['score'], "param2":request.form['review'], "param3":request.form['review_id']})
        )
        db.commit()
    return redirect(url_for('show_book', isbn= request.form['isbn']))

@app.route('/create_review', methods = ['GET','POST'])
def create_review():
    print(request.form)
    id = session['user_id']
    if request.method == 'POST':        
        db.execute(
            "INSERT INTO reviews (isbn, user_id, score, review) "
            "VALUES (:isbn, :user_id, :score, :review)",
            ({"isbn":request.form['isbn'], "user_id":id, "score":request.form['score'], "review":request.form['review']})
        )
        db.commit()
    return redirect(url_for('show_book', isbn= request.form['isbn']))


if __name__== '__main__':

    app.run()
