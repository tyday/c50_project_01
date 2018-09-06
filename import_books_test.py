# using sqlalchemy tips from 
# https://www.compose.com/articles/using-postgresql-through-sqlalchemy/
# and csv tips from
# https://docs.python.org/3/library/csv.html
import csv, config
from sqlalchemy import create_engine
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


db_string = config.DATABASE_URL

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
books = session.query(Book)
for book in books:
    i += 1
    print(book.title, book.year, i)  