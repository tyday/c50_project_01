# using sqlalchemy tips from 
# https://www.compose.com/articles/using-postgresql-through-sqlalchemy/
# and csv tips from
# https://docs.python.org/3/library/csv.html
import csv, config
from sqlalchemy import create_engine
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


db_string = config.db_key

db = create_engine(db_string)
base = declarative_base()

class Book(base):
    __tablename__ = 'books'

    isbn = Column(String, primary_key=True)
    title = Column(String)
    author = Column(String)
    year = Column(String)

Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)


i=0
with open('books.csv', newline='') as csvfile:
    bookreader = csv.reader(csvfile)
    for row in bookreader:
        if i != 0:
            # print(row)
            book_entry = Book(isbn=row[0], title=row[1], author=row[2], year=row[3])
            session.add(book_entry)
            session.commit()
        i += 1
# This was very slow. There is probably a way to commit multiple additions to the Db 
# 
# I want to do a test where i look through the CSV and check to see if there is a matching isbn as well as title etc.      