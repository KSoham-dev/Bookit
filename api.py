from flask import Flask,jsonify
from flask_restful import Resource, Api, reqparse
from models import *
import base64,json,os
import matplotlib.pyplot as plt
from io import BytesIO
import matplotlib
import random
matplotlib.use('agg')
parser = reqparse.RequestParser()
parser.add_argument("name")
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.sqlite3"
db.init_app(app)
api = Api(app)
app.app_context().push()
parser = reqparse.RequestParser()
parser.add_argument("book_name")
parser.add_argument("book_description")
parser.add_argument("book_price")
parser.add_argument("book_content_base64_encoded")
parser.add_argument("book_section_id")
parser.add_argument("book_author_ids")
parser.add_argument("section_name")
parser.add_argument("section_description")
parser.add_argument("author_name")
parser.add_argument("author_description")
class BookAPI(Resource):
    def get(self):
        all_books = {}
        books = Book.query.all() 
        j=0 
        for book in books:
            bk={}
            d_fb = {}
            i,k=0,0
            aut={}
            pdf_file = open('./static/book_content_pdf/'+book.content,'rb')
            pdf_bytes = pdf_file.read() 
            content = base64.b64encode(pdf_bytes).decode('utf-8')
            jsonify(content=content)
            
            bk['book_id'] = book.book_id
            bk['book_name'] = book.book_name
            bk['book_description'] = book.book_description
            bk['book_content_base64_encoded'] = content
            bk['book_section'] = book.section_id
            bk['book_price'] = book.price
            for author in book.author:
                i+=1
                aut[f'author_{i}'] = author.author_name
                bk['book_authors'] = aut
            fb = db.session.execute(select(feedback)).all()
            for f in fb:
                if f[0] == book.book_id:
                    k+=1
                    d_fb[f'feedback{k}'] = f[2]
                    bk['book_feedbacks'] = d_fb
            j+=1
            all_books[f"book_{j}"] = bk
        return all_books
    def put(self,book_id):
        book_id_list,name=[],[]
        args = parser.parse_args()
        book_name = args["book_name"]
        book_price = args["book_price"]
        book_description = args["book_description"]
        book_author_ids = args["book_author_ids"]
        book_section_id = args["book_section_id"]
        book_content = args["book_content_base64_encoded"]
        for book in Book.query.all():
            book_id_list.append(book.book_id)
        if book_id not in book_id_list:
            return "Book not found",404
        else:
            book = db.session.get(Book, book_id)
            if book_name:
                book.book_name = book_name
                db.session.commit()
                name.append('book_name')
            if book_description:
                book.book_description = book_description
                db.session.commit()
                name.append('book_description')
            if book_section_id:
                secid_list=[]
                book_section_id = int(book_section_id)
                for s in Section.query.all():
                    secid_list.append(s.section_id)
                if book_section_id in secid_list:
                    book.section_id = book_section_id
                    db.session.commit()
                    name.append('book_section_id')
                else:
                    return "Section not found",404
            if book_price:
                book.price = int(book_price)
                db.session.commit()
                name.append('book_price')
            if book_author_ids:
                aut_ids,flag,allautid_list = list(json.loads(book_author_ids.replace("'", "\"")).values()), False, []
                for a in Author.query.all():
                    allautid_list.append(a.author_id)
                for i in aut_ids:
                    if i in allautid_list:
                        flag = True
                    else:
                        return "Author not found",404
                        break
                if flag:
                    auths = Author.query.filter(Author.author_id.in_(aut_ids)).all()
                    book.author = auths
                    db.session.commit()
                    name.append('book_authors')
            if book_content:
                try:
                    base64.b64encode(base64.b64decode(book_content))
                    os.remove(f'./static/book_content_pdf/{book.content}')
                    b = book_content
                    bytes = base64.b64decode(b, validate=True)
                    book_name = db.session.get(Book, book_id).book_name
                    book.content = f'{book_name}.pdf'
                    db.session.commit()
                    with open(f'./static/book_content_pdf/{book_name}.pdf', 'wb') as f:
                        f.write(bytes) 
                    name.append('book_content')
                except Exception:
                    return "Wrong encoding format, Check again !!!",500
            return(f'{name} updated successfully')
    def post(self):
        args = parser.parse_args()
        book_name = args["book_name"]
        book_price = args["book_price"]
        book_description = args["book_description"]
        book_author_ids = args["book_author_ids"]
        book_section_id = args["book_section_id"]
        book_content = args["book_content_base64_encoded"]
        if book_name is None:
            return {"Error": "Book name not supplied"},500
        if book_description is None:
            return {"Error": "Book description not supplied"},500
        if book_content is None:
            return {"Error": "Book content not supplied"},500
        if book_price is None:
            return {"Error": "Book price not supplied"},500
        if book_author_ids is None:
            return {"Error": "Book authors not supplied"},500
        if book_section_id is None:
            return {"Error": "Book section not supplied"},500
        try:
            base64.b64encode(base64.b64decode(book_content))
            b = book_content
            bytes = base64.b64decode(b, validate=True)
            content = f'{book_name}.pdf'
            secid_list=[]
            for s in Section.query.all():
                secid_list.append(s.section_id)
            try:
                book_section_id = int(book_section_id)
            except Exception:
                return "Enter correct section id ",500
            if book_section_id not in secid_list:
                return "Section not found",404
            with open(f'./static/book_content_pdf/{book_name}.pdf', 'wb') as f:
                f.write(bytes)
            book = Book(book_name=book_name, price=book_price, book_description=book_description, section_id=book_section_id, content=content)
            db.session.add(book)
            aut_ids,flag1,allautid_list = list(json.loads(book_author_ids.replace("'", "\"")).values()), False, []
            for a in Author.query.all():
                allautid_list.append(a.author_id)
            for i in aut_ids:
                try:
                    i = int(i)
                except Exception:
                    return "Enter correct author id ",500
                if i in allautid_list:
                    flag1 = True
                else:
                    return "Author not found",404
                    break
            if flag1:
                auths = Author.query.filter(Author.author_id.in_(aut_ids)).all()
                book.author = auths
                db.session.commit()
            return "Added Book Successfully",200
        except Exception:
                    return "Wrong encoding format, Check again !!!",500

    def delete(self, book_id):
        book = db.session.get(Book, book_id)
        book_ids = []
        books = Book.query.all()
        for bk in books:
            book_ids.append(bk.book_id)
        if book_id not in book_ids:
            return "Book not found",404
        db.session.delete(book)
        os.remove(f'./static/book_content_pdf/{book.content}')
        db.session.commit()
        return "Deleted successfully",200

class SectionAPI(Resource):
    def get(self):
        sections = Section.query.all()
        d_sec,i = {},0
        for section in sections:
            i+=1
            d_in,books_in_sec,j = {},{},0
            d_in['section_id']  = section.section_id
            d_in['section_name'] = section.section_name
            d_in['section_description'] = section.section_description
            d_in['section_date_created'] = str(section.date_created.date())
            for bk in section.books:
                j+=1
                books_in_sec[f'book_{j}'] = bk.book_name
            d_in['section_books'] = books_in_sec
            d_sec[f'section_{i}'] = d_in
        return d_sec,200

    def put(self, section_id):
        args = parser.parse_args()
        section_name = args["section_name"]
        section_description = args["section_description"]
        section = db.session.get(Section, section_id)
        section_ids,sections,l=[],Section.query.all(),[]
        for s in sections:
            section_ids.append(s.section_id)
        if section_id not in section_ids:
            return "Section not found",404
        if section_name:
            section.section_name = section_name
            db.session.commit()
            l.append("section_name")
        if section_description:
            section.section_description=section_description
            db.session.commit()
            l.append("section_description")
        if l:
            return f"{l} updated successfully",200
        else:
            return "No Data",500
    def delete(self,section_id):
        section_ids,sections=[],Section.query.all()
        for s in sections:
            section_ids.append(s.section_id)
        if section_id not in section_ids:
            return "Section not found",404
        section = db.session.get(Section, section_id)
        db.session.delete(section)
        db.session.commit()
        return "Section deleted successfully",200
    def post(self):
        args = parser.parse_args()
        section_name = args["section_name"]
        section_description = args["section_description"]
        if section_name is None:
            return "Section name not provided",500
        if section_description is None:
            return "Section description not provided",500
        section = Section(section_name=section_name, section_description=section_description)
        db.session.add(section)
        db.session.commit()
        return "Successfully added section",200

class AuthorAPI(Resource):
    def get(self):
        authors = Author.query.all()
        a_dict,i={},0
        for a in authors:
            i+=1
            a_in = {}
            a_in["author_id"] = a.author_id
            a_in["author_name"] = a.author_name
            a_in["author_description"] = a.author_description
            a_dict[f"author_{i}"] = a_in
        return a_dict,200
    def put(self, author_id):
        args = parser.parse_args()
        author_name = args["author_name"]
        author_description = args["author_description"]
        allautid_list=[]
        for a in Author.query.all():
                allautid_list.append(a.author_id)
        author=db.session.get(Author, author_id)
        if author_id not in allautid_list:
            return "Author not found",404
        l=[]
        if author_name:
            author.author_name=author_name
            db.session.commit()
            l.append("author_name")
        if author_description:
            author.author_description=author_description
            db.session.commit()
            l.append("author_description")
        if l:
            return f"{l} updated successfully",200
        else:
            return "No Data",500
    def post(self):
        args = parser.parse_args()
        author_name = args["author_name"]
        author_description = args["author_description"]
        if author_name is None:
            return "Author name not supplied",500
        if author_description is None:
            return "Author description not supplied",500
        author = Author(author_name=author_name, author_description=author_description)
        db.session.add(author)
        db.session.commit()
        return "Author added successfully",200
    def delete(self, author_id):
        allautid_list=[]
        for a in Author.query.all():
                allautid_list.append(a.author_id)
        author=db.session.get(Author, author_id)
        if author_id not in allautid_list:
            return "Author not found",404
        db.session.delete(author)
        db.session.commit()
        return "Author deleted successfully",200

class GraphAPI(Resource):
    def get(self,dist):
        def issued_dist():
            d1={}
            for section in Section.query.all():
                d1[section.section_name] = 0
            for user in User.query.all():
                for book in user.books_owned:
                    sec = db.session.get(Section, book.section_id).section_name
                    d1[sec] += 1
            colors = [plt.cm.Dark2(random.random()) for _ in range(len(d1))]
            plt.bar(d1.keys(),d1.values(),color=colors)
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            return f"<img src='data:image/png;base64,{data}'/>"

        def books_dist():
            d={}
            for section in Section.query.all():
                d[section.section_name] = len(section.books)
            fig = plt.figure(figsize=(10, 7))
            plt.pie(d.values(), labels=d.keys(), radius=1.5, autopct='%1.1f%%')
            plt.pie([1],colors="w")
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            return f"<img src='data:image/png;base64,{data}'/>"
            
        if dist == "book_dist":
            return books_dist()
            
        if dist == "issued_dist":
            return issued_dist()
    def put(self,dist):
         return "Method not allowed",500
    def post(self,dist):
         return "Method not allowed",500  
    def delete(self,dist):
         return "Method not allowed",500  

api.add_resource(BookAPI,'/api/books', '/api/book/<int:book_id>')
api.add_resource(SectionAPI,'/api/sections', '/api/section/<int:section_id>')
api.add_resource(AuthorAPI,'/api/authors', '/api/author/<int:author_id>')
api.add_resource(GraphAPI,'/api/graphs/<dist>')

if __name__ == "__main__":
    app.run(debug = True)