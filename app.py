from flask import Flask, render_template, request, redirect, url_for, send_file, after_this_request, abort
from models import *
from werkzeug.utils import secure_filename
import zipfile,os,matplotlib,random
from functools import wraps
import matplotlib.pyplot as plt
matplotlib.use('agg')
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.sqlite3"
db.init_app(app)
app.app_context().push()

id_list,bkid_list,secid_list,autid_list = [],[],[],[]
for u in User.query.all():
    id_list.append(u.usr_id)
for b in Book.query.all():
    bkid_list.append(b.book_id)
for s in Section.query.all():
    secid_list.append(s.section_id)
for a in Author.query.all():
    autid_list.append(a.author_id)


@app.route("/", methods=['GET','POST'])
def user_login():
    if request.method == 'POST':
        em=request.form.get("lemail")
        usr = User.query.filter_by(email=em).first()
        if (usr in User.query.all()):
            if (request.form.get("lpass") == User.query.filter_by(email=em).first().password):
                if(usr.role=='user'):
                    usr.login()
                    return redirect(url_for('home', user_id=usr.usr_id))
                else:
                    return render_template("unauthorized.html")

            else:
                return render_template("wrongdetails.html")
        else:
            return render_template("wrongdetails.html")
    return render_template('user_login.html')



@app.route("/lib/login", methods=['GET','POST'])
def lib_login():
    if request.method == 'POST':
        em=request.form.get("lemail")
        usr = User.query.filter_by(email=em).first()
        if (usr in User.query.all()):
            if (request.form.get("lpass") == User.query.filter_by(email=em).first().password):
                if(usr.role == "librarian"):
                    usr.login()
                    return redirect(url_for("lib_profile",user_id=usr.usr_id))
                else:
                    return render_template("unauthorized.html")
            else:
                return render_template("wrongdetails.html")
        else:
            return render_template("wrongdetails.html")
    return render_template("lib_login.html")


@app.route("/user/signup", methods=['GET','POST'])
def user_signup():
    if request.method == "POST":
        em = request.form.get("supemail")
        fname = request.form.get("supfname")
        lname = request.form.get("suplname")
        passw = request.form.get("suppass")  
        new_user  = User(email=em, f_name=fname, l_name=lname, password=passw, role="user")
        db.session.add(new_user)
        db.session.commit()
        if new_user.usr_id not in id_list:
            id_list.append(new_user.usr_id)
        return redirect(url_for('user_login'))
     
    return render_template("user_signup.html")


@app.route("/<int:user_id>/home")
def home(user_id):
    if user_id in id_list:
        user = db.session.get(User,user_id)
        if user.is_active:
            books = Book.query.all()
            sections= Section.query.all()
            return render_template("home.html",user=user,user_id=user_id,books=books,sections=sections)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:user_id>/profile", methods=['GET' , 'POST'])
def user_profile(user_id):
    if user_id in id_list:
        user = db.session.get(User,user_id)
        if user.is_active:
            if request.method == "POST":
                if (request.form.get("uptpass") == usr.password):
                    usr.f_name = request.form.get("uptfname")
                    usr.l_name = request.form.get("uptlname")
                    db.session.commit()
            return  render_template("user_profile.html", user=user)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:user_id>/books")
def user_books(user_id):
    if user_id in id_list:
        user=db.session.get(User, user_id)
        if user.is_active:
            books=user.books_owned
            isb = db.session.execute(select(issued_books)).all()
            cur_date=datetime.utcnow().date()
            l=[]            
            for i in isb:
                if user_id == i[0]:
                    l.append([i[0],db.session.get(Book, i[1]).book_id,(cur_date-i[2].date()).days])
            return render_template("user_books.html",books=books,user=user,l=l)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:user_id>/user/return_book/<int:book_id>")
def return_book(user_id,book_id):
    
    user = db.session.get(User, user_id)
    books_owned = user.books_owned
    for book in books_owned:
        if (book.book_id == book_id):
            user.books_owned.remove(book)
            db.session.commit()
            return redirect(request.referrer)
        else:
            redirect(f'/{user_id}/books')

@app.route("/<int:user_id>/books/<int:book_id>")
def view_book_info(book_id,user_id):
    if user_id in id_list:
        user = db.session.get(User, user_id)
        if book_id in bkid_list:
            if user.is_active:
                book = db.session.get(Book, book_id)
                users = User.query.all()
                d,flag={},False
                fb = db.session.execute(select(feedback)).all()
                for i in fb:
                    if (i[0] == book.book_id): 
                        d[db.session.get(User, i[1])] =  i[2]  
                if (db.session.get(User, user_id) in d.keys()):
                    flag = True   
                return render_template("view_book_info.html",book=book,user=user,d=d,flag=flag)
            else:
                abort(401)
        else:
            abort(404,"Book Not Found")
    else:
        abort(404,"User Not Found")

@app.route("/<int:user_id>/request/<int:book_id>")
def req_book(user_id,book_id):
    user=db.session.get(User, user_id)
    book=db.session.get(Book, book_id)
    user.books_requested.append(book)
    db.session.commit()
    return redirect(url_for("view_req_books", user_id=user_id))

@app.route("/<int:user_id>/books_req")
def view_req_books(user_id):
    if user_id in id_list:
        user=db.session.get(User, user_id)
        if user.is_active:
            books=user.books_requested
            return render_template("view_req_books.html",books=books,user=user)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:user_id>/user/withdraw_req/<int:book_id>")
def withdraw_books(user_id,book_id):
    user = db.session.get(User, user_id)
    books_req= user.books_requested
    for book in books_req:
        if (book.book_id == book_id):
            user.books_requested.remove(book)
            db.session.commit()
            return redirect(request.referrer)
        else:
            redirect(f"/{user_id}/books_req")

@app.route("/lib/<int:user_id>/profile", methods=['GET' , 'POST'])
def lib_profile(user_id):
    if user_id in id_list:
        usr = db.session.get(User,user_id)
        if usr.role == "librarian":
            if usr.is_active:
                if request.method == "POST":
                    if (request.form.get("uptpass") == usr.password):
                        usr.f_name = request.form.get("uptfname")
                        usr.l_name = request.form.get("uptlname")
                        db.session.commit()
                return  render_template("lib_profile.html", user_id=user_id, user=usr)
            else:
                abort(401)
        else:
                abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:user_id>/all_books")
def all_books(user_id):
    if user_id in id_list:
        user = db.session.get(User,user_id)
        if user.role == "librarian":
            if user.is_active:
                books = Book.query.all()
                Sections = Section.query.all()
                d={}
                for section in Sections:
                    d[section.section_id]=section.section_name
                return render_template("all_books.html",user=user,books=books,d=d)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:book_id>/remove_book")
def remove_book(book_id):
    book=db.session.get(Book, book_id)
    db.session.delete(book)
    os.remove('./static/book_content_pdf/'+book.content)
    db.session.commit()
    return redirect(request.referrer)

@app.route("/user/<int:user_id>/<int:book_id>/update_book", methods=['GET' , 'POST'])
def update_book(user_id,book_id):
    if user_id in id_list:
        usr = db.session.get(User,user_id)
        if usr.role == "librarian":
            if usr.is_active:
                if book_id in bkid_list:
                    book=db.session.get(Book, book_id)
                    sections=Section.query.all()
                    authors=Author.query.all()
                    if request.method == "POST":
                        name = request.form.get("uptname")
                        desc = request.form.get("uptdesc")
                        sec = request.form.get("section")
                        pri = request.form.get("uptprice")
                        auth_ids = request.form.getlist("authors")
                        file = request.files['pdf']
                        if name:
                            book.book_name = name
                        if desc:
                            book.book_description = desc
                        if sec:
                            book.section_id = sec
                        if pri:
                            book.price = pri
                        if auth_ids:
                            auths = Author.query.filter(Author.author_id.in_(auth_ids)).all()
                            book.author = auths
                        if file:
                            os.remove('./static/book_content_pdf/'+book.content)
                            fname = secure_filename(file.filename)
                            path='./static/book_content_pdf/' + fname
                            file.save(path)
                            book.content = fname
                        db.session.commit()
                        return redirect(url_for("all_books",user_id=user_id))
                    return  render_template("update_book.html", user=usr, book=book, sections=sections, authors=authors)
                else:
                    abort(404,"Book Not Found")
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/user/<int:user_id>/add_book", methods=['GET' , 'POST'])
def add_book(user_id):
    if user_id in id_list:
        usr = db.session.get(User,user_id)
        if usr.role == "librarian":
            if usr.is_active:
                sections=Section.query.all()
                authors=Author.query.all()
                if request.method == "POST":
                    auth_ids = request.form.getlist("authors")
                    file = request.files['pdf']
                    book_name = request.form.get("name")
                    book_description = request.form.get("desc")
                    section_id = request.form.get("section")
                    price = request.form.get("price")
                    auths = Author.query.filter(Author.author_id.in_(auth_ids)).all()
                    authors = auths
                    fname = secure_filename(file.filename)
                    path=f'./static/book_content_pdf/{fname}'
                    file.save(path)
                    content = fname
                    book=Book(book_name=book_name,book_description=book_description,section_id=section_id,price=price,content=content)
                    db.session.add(book)
                    db.session.commit()
                    if book.book_id not in bkid_list:
                        bkid_list.append(book.book_id)
                    for author in auths:
                        book.author.append(author)
                    db.session.commit()
                    return redirect(url_for("all_books",user_id=user_id))
                return  render_template("add_book.html", user=usr, sections=sections, authors=authors)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:book_id>/read_book")
def read_book(book_id):
    if book_id in bkid_list:
        book=db.session.get(Book, book_id)
        return render_template("read_book.html",book=book)
    else:
        abort(404,"Book Not Found")

@app.route("/buy/<int:book_id>")
def buy_book(book_id):
    book=db.session.get(Book, book_id)
    return render_template("buy_book.html",book=book)

@app.route("/<int:user_id>/lib/see_req_lib")
def see_req_lib(user_id):
    if user_id in id_list:
        librarian = db.session.get(User,user_id)
        if librarian.role == "librarian":
            if librarian.is_active:
                users = User.query.all()
                return render_template("see_req_lib.html",users=users,user=librarian)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:user_id>/user/<int:book_id>/approve_book")
def approve_book(user_id,book_id):
    user=db.session.get(User,user_id)
    book=db.session.get(Book,book_id)
    user.books_owned.append(book)
    user.books_requested.remove(book)
    db.session.commit()
    return redirect(request.referrer)

@app.route("/<int:user_id>/lib/sections")
def all_sections(user_id):
    if user_id in id_list:
        librarian=db.session.get(User, user_id)
        if librarian.role == "librarian":
            if librarian.is_active:
                sections=Section.query.all()
                return render_template("view_section.html",sections=sections,user=librarian)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:section_id>/remove_section")
def reomve_section(section_id):
    section=db.session.get(Section, section_id)
    db.session.delete(section)
    db.session.commit()
    return redirect(request.referrer)

@app.route("/lib/<int:user_id>/<int:section_id>/update_section",methods=["GET","POST"])
def update_section(user_id,section_id):
    if user_id in id_list:
        librarian=db.session.get(User, user_id)
        if librarian.role == "librarian":
            if librarian.is_active:
                if section_id in secid_list:
                    section = db.session.get(Section, section_id)
                    if request.method == "POST":
                        section.section_name = request.form.get("uptname")
                        section.section_description = request.form.get("uptdesc")
                        db.session.commit()
                        return redirect(url_for("all_sections",user_id=user_id))
                    return render_template("update_section.html",user=librarian,section=section)
                else:
                    abort(404, "Section Not Found")
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/lib/<int:user_id>/add_section",methods=["GET","POST"])
def add_section(user_id):
    if user_id in id_list:
        librarian=db.session.get(User, user_id)
        if librarian.role == "librarian":
            if librarian.is_active:
                if request.method == "POST":
                    sn= request.form.get("uptname")
                    sd = request.form.get("uptdesc")
                    section=Section(section_name=sn,section_description=sd)
                    db.session.add(section)
                    db.session.commit()
                    if section.section_id not in secid_list:
                        secid_list.append(section.section_id)
                    return redirect(url_for("all_sections",user_id=user_id))
                return render_template("add_section.html",user=librarian)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:user_id>/lib/books_issued")
def view_book_issued_lib(user_id):
    if user_id in id_list:
        librarian=db.session.get(User, user_id)
        if librarian.role == "librarian":
            if librarian.is_active:
                users=User.query.all()
                books = Book.query.all()
                isb = db.session.execute(select(issued_books)).all()
                cur_date=datetime.utcnow().date()
                l=[[i[0],db.session.get(Book, i[1]),(cur_date-i[2].date()).days] for i in isb]
                return render_template("view_book_issued_lib.html", user=librarian, isb=isb,l=l,users=users)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:user_id>/search", methods=["GET","POST"])
def search_for(user_id):
    books = Book.query.all()
    sections = Section.query.all()
    authors = Author.query.all()
    user = db.session.get(User, user_id)
    if request.method == "POST":
        item = request.form.get("search")
        item = "%".join(item.split())
        results = Book.query.filter(db.func.replace(Book.book_name, ' ', '').ilike('%' + bindparam('item') + '%')).params(item=item).all()
        if results==[]:
            results = Section.query.filter(db.func.replace(Section.section_name, ' ', '').ilike('%' + bindparam('item') + '%')).params(item=item).all()
        if results==[]:
            results = Author.query.filter(db.func.replace(Author.author_name, ' ', '').ilike('%' + bindparam('item') + '%')).params(item=item).all()
        flag_books = set(results).issubset(set(books))
        return render_template("search.html",results=results,books=books,authors=authors,sections=sections,user=user,flag_books=flag_books)

@app.route("/<int:user_id>/cart")
def cart(user_id):
    user=db.session.get(User, user_id)
    if user.is_active:
        cart=Cart.query.filter_by(user_id=user_id).all()
        if cart:
            products=cart[0].book
        else:
            products=[]
        return render_template("cart.html",user=user,cart=cart,products=products)
    else:
        abort(401)

@app.route("/bulk_buy",methods=['GET','POST'])
def bulk_buy():
    if request.method=="POST":
        lis=request.form.getlist("cart")
    return render_template("bulk_buy.html",lis=lis)

@app.route("/download",methods=['GET','POST'])
def download_bulk():
    if request.method=="POST":
        products=request.form.getlist("cart")
        files = [f'./static/book_content_pdf/{p}' for p in products]
        books = zipfile.ZipFile('./static/book_content_pdf/books.zip', 'w')
        for file in files:
            books.write(file)
        books.close()
        return send_file('./static/book_content_pdf/books.zip', as_attachment=True)

@app.route("/<int:user_id>/create_cart")
def create_cart(user_id):
    user = db.session.get(User, user_id)
    cart=Cart(user_id=user_id)
    db.session.add(cart)
    db.session.commit()
    return redirect(request.referrer)

@app.route("/<int:user_id>/add_to_cart/<int:book_id>")
def add_to_cart(user_id,book_id):
    user=db.session.get(User, user_id)
    book=db.session.get(Book, book_id)
    cart=Cart.query.filter_by(user_id=user_id).all()
    if cart:  
        if book not in cart[0].book:
                cart[0].book.append(book)
                db.session.commit()
        return redirect(url_for("cart",user_id=user_id))
    else:
        return redirect(url_for("cart",user_id=user_id))

@app.route("/<int:user_id>/remove_from_cart/<int:book_id>")
def remove_from_cart(user_id,book_id):
    user=db.session.get(User, user_id)
    book=db.session.get(Book, book_id)
    cart=Cart.query.filter_by(user_id=user_id).all()
    cart[0].book.remove(book)
    db.session.commit()
    return redirect(url_for("cart",user_id=user_id))

@app.route("/<int:user_id>/lib/authors")
def view_authors(user_id):
    if user_id in id_list:
        librarian=db.session.get(User, user_id)
        if librarian.role == "librarian":
            if librarian.is_active:
                authors=Author.query.all()
                return render_template("view_authors.html",authors=authors,user=librarian)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:author_id>/remove_author")
def remove_author(author_id):
    author = db.session.get(Author, author_id)
    db.session.delete(author)
    db.session.commit()
    return redirect(request.referrer)

@app.route("/<int:user_id>/lib/<int:author_id>/update_author",methods=["GET","POST"])
def update_author(user_id,author_id):
    if user_id in id_list:
        librarian=db.session.get(User, user_id)
        if librarian.role == "librarian":
            if librarian.is_active:
                if author_id in autid_list:
                    author = db.session.get(Author, author_id)
                    if request.method == "POST":
                        author.author_name = request.form.get("uptname")
                        author.author_description = request.form.get("uptdesc")
                        db.session.commit()
                        return redirect(url_for("view_authors",user_id=user_id))
                    return render_template("update_author.html",user=librarian,author=author)
                else:
                    abort(404,"Author Not Found")
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:user_id>/lib/add_author",methods=["GET","POST"])
def add_author(user_id):
    if user_id in id_list:
        librarian=db.session.get(User, user_id)
        if librarian.role == "librarian":
            if librarian.is_active:
                if request.method == "POST":
                    author_name = request.form.get("addname")
                    author_description = request.form.get("adddesc")
                    author = Author(author_name=author_name,author_description=author_description)
                    db.session.add(author)
                    db.session.commit()
                    if author.author_id not in autid_list:
                        autid_list.append(author.author_id)
                    return redirect(url_for("view_authors",user_id=user_id))
                return render_template("add_author.html",user=librarian)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:user_id>/lib/stats")
def statistics(user_id):
    if user_id in id_list:
        librarian=db.session.get(User, user_id)
        if librarian.role == "librarian":
            if librarian.is_active:
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
                    plt.savefig('./static/issued_dist.png', format='png')
                    plt.close()
                def books_dist():
                    d={}
                    for section in Section.query.all():
                        d[section.section_name] = len(section.books)
                    fig = plt.figure(figsize=(10, 7))
                    plt.pie(d.values(), labels=d.keys(), radius=1.5, autopct='%1.1f%%')
                    plt.pie([1],colors="w")
                    plt.savefig('./static/book_dist.png', format='png')
                    plt.close()
                issued_dist()
                books_dist()
                return render_template("statistics.html", user=librarian)
            else:
                abort(401)
        else:
            abort(401)
    else:
        abort(404,"User Not Found")

@app.route("/<int:user_id>/<int:book_id>/add_feedback", methods=['GET','POST'])
def add_feedback(user_id,book_id):
    if request.method == "POST":
        fdb = request.form.get("feedback")
        db.session.execute(feedback.insert().values(usr_id=user_id, book_id=book_id, feedback=fdb))
        db.session.commit()
        return redirect(f"/{user_id}/books/{book_id}")
    user = db.session.get(User, user_id)
    book = db.session.get(Book, book_id)
    return render_template("add_feedback.html",user=user,book=book)

@app.route("/<int:user_id>/<int:book_id>/remove_feedback")
def remove_feedback(user_id,book_id):
    user = db.session.get(User, user_id)
    book = db.session.get(Book, book_id)
    feedbacks = book.feedbacks
    for feedback in feedbacks:
        if (user_id == feedback.usr_id):
            feedbacks.remove(feedback)
            db.session.commit()
    return redirect(request.referrer)

@app.route("/<int:user_id>/logout")
def logout(user_id):
    usr = db.session.get(User, user_id)
    usr.logout()
    return redirect(url_for('user_login'))

@app.route("/about")
def about_us():
    return render_template("about_us.html")

if __name__ == "__main__":
    app.run(debug = True)


