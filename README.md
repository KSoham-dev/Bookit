# Bookit
## A minimalistic e-library application
The project discussed below aims to provide an interface for an e-library (i.e. a Library
Management System). This application can be used by both users and librarians. Users can
request, read and buy books (PDF files) with some restrictions as specified by the guideline
document (The user can request utmost 5 books at a time and also a user can access a book
maximum for 15 days after which access to the book will be revoked). The user also has a cart
functionality through which he can buy many books in a single click. On the other a librarian has
more authority such as updating/adding books, sections, authors and accessing some statistics
about the application. Both users and the librarian have separate login systems where a user
can sign up too, RBAC is used to differentiate between user and librarian. This app is developed
keeping in mind factors such as ease of access, minimalistic styling and minimal complexities
(like adding buttons and links only when required, easy search etc.). For the storage purpose
sqlite3 has been used but for storage of book content a different approach has been used
wherein the pdf files are directly stored in the server and only the filename is stored in the
database, this allows ease of displaying book content and downloading the book as pdf too.
Various models are used in order to store different information about different components of the
app. As part of the project a REST API’s are developed for the Books, Sections, Authors and
Graphs to get, update, add or delete book, section or author. The graph API has only a GET
method allowed so graphs can be fetched using it.

### Technology Stack:  
[![My Skills](https://skillicons.dev/icons?i=html,css,bootstrap,flask,sqlite)](https://skillicons.dev)  
- HTML: Used for creating templates
- CSS: Used for styling web pages
- Bootstrap: A simple yet powerful framework used for styling minimalistic web pages
- Flask: An python library for developing backend of the web applications
    - Flask-RESTful: An extension for flask used to develop API’s
    - Flask-SQLAlchemy: An extension for flask used to integrate SQLAlchemy with flask
- SQLite: It is a database engine

### Author: Soham S. Kulkarni 
### Contact: sohamkulkarni709@gmail.com
