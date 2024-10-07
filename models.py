from flask_sqlalchemy import SQLAlchemy as sq
from datetime import datetime
from sqlalchemy import select
from sqlalchemy import bindparam


db = sq()

#One user can have many books issued and vice-versa
issued_books = db.Table('issued_books', 
    db.Column('usr_id', db.Integer, db.ForeignKey('user.usr_id', ondelete='CASCADE') ),
    db.Column('book_id', db.Integer, db.ForeignKey('book.book_id', ondelete='CASCADE')),
    db.Column('issue_date', db.DateTime, default=datetime.utcnow),
    db.Column('return_date', db.DateTime))

#One user can have many books requested and vice-versa
requested_books = db.Table('requested_books', 
    db.Column('usr_id', db.Integer, db.ForeignKey('user.usr_id', ondelete='CASCADE')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.book_id', ondelete='CASCADE')))

#One book can have many authors and vice-versa
book_authored = db.Table('book_authored',
    db.Column('author_id', db.Integer, db.ForeignKey('author.author_id', ondelete='CASCADE')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.book_id', ondelete='CASCADE')))  

#One book can be in many carts and vice-versa
product = db.Table('product',
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.cart_id', ondelete='CASCADE')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.book_id', ondelete='CASCADE')))

#One book can have many feedbacks and One user can give many feedbacks 
feedback = db.Table('feedback',
    db.Column('book_id', db.Integer, db.ForeignKey('book.book_id', ondelete='CASCADE')),
    db.Column('usr_id', db.Integer, db.ForeignKey('user.usr_id', ondelete='CASCADE')),
    db.Column('feedback', db.String(500)))

class User(db.Model):
    usr_id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(30), nullable=False)
    l_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    books_owned = db.relationship('Book', secondary=issued_books, backref='owner')
    books_requested = db.relationship('Book', secondary=requested_books, backref='requester')
    cart = db.relationship('Cart', backref='owner', uselist=False  ) # One user can have only one cart and vice-versa
    def login(self):
        self.is_active = True
        db.session.commit()
    def logout(self):
        self.is_active = False
        db.session.commit()

class Section(db.Model):
    section_id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(50), nullable=False)
    section_description = db.Column(db.String(250), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    books = db.relationship('Book', backref='section'  ) #One section can have many books but one books can be present only in one section

class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(50), nullable=False)
    book_description = db.Column(db.String(250), nullable=False)
    content = db.Column(db.String, nullable=False, unique=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section.section_id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    feedbacks = db.relationship('User', secondary=feedback, backref='user')
    

class Author(db.Model):
    author_id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(50), nullable=False)
    author_description = db.Column(db.String(250))
    books = db.relationship('Book', secondary=book_authored, backref='author')

class Cart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id =  db.Column(db.Integer, db.ForeignKey('user.usr_id',ondelete='CASCADE'), unique=True)
    book = db.relationship('Book', secondary=product, backref='product')





