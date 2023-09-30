from flask import Flask, render_template, request, redirect, url_for, abort, g
import sqlite3
import datetime

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def obtenir_categories():
    categories = []
    myresult = query_db("SELECT * FROM categories")
    for x in myresult:
        categories.append(x)
    return categories

def obtenir_producte_id(id):
    myresult = query_db("SELECT * FROM products WHERE id = ?", (id,))
    return myresult

@app.route("/")
def hello_world():
    return render_template('HelloWorld.html')

@app.route('/products/list')
def products_list():
    products = query_db("SELECT * FROM products")
    return render_template('products/list.html', results=products)

@app.route('/products/read/<int:id>')
def products_read(id):
    product = obtenir_producte_id(id)
    if not product:
        abort(404)
    categories = obtenir_categories()
    return render_template('products/read.html', results=product, categories=categories)

@app.route('/products/create', methods=["GET", "POST"])
def products_create():
    if request.method == 'GET':
        categories = obtenir_categories()
        return render_template('products/create.html', results=categories)
    elif request.method == 'POST':
        data = request.form
        if all(data.values()):
            mydb = get_db()
            mycursor = mydb.cursor()
            dia_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "INSERT INTO products (title, description, photo, price, category_id, seller_id, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            # Pasa los valores como una tupla en la sentencia SQL
            mycursor.execute(sql, (data['title'], data['description'], data['photo'], data['price'], data['category_id'], 10, dia_actual, dia_actual))
            mydb.commit()
            return redirect(url_for('products_list'))
    abort(404)

#     elif request.method == 'POST':
#             data = request.form
#             if data['title'] != "" and data['description'] != "" and data['photo'] != "" and data['price'] != "":
#                 mydb = get_db()
#                 mycursor = mydb.cursor()
#                 dia = datetime.datetime.now()
#                 dia_actual = dia.strftime("%Y-%m-%d %H:%M:%S")
#                 sql = "INSERT INTO products (title, description, photo, price, category_id, seller_id, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
#                 mycursor.execute(sql, (data['title'], data['description'], data['photo'], data['price'], data['category_id'], 111, dia_actual, dia_actual))
#                 mydb.commit()
#                 return redirect(url_for('products_list'))
#             else:
#                 return redirect(url_for('hello_world'))
#     else:
#         abort(404)

@app.route('/products/update/<int:id>', methods=["GET", "POST"])
def products_update(id):
    product = obtenir_producte_id(id)
    if not product:
        abort(404)
    
    if request.method == 'GET':
        categories = obtenir_categories()
        return render_template('products/update.html', results=product, categories=categories)
    elif request.method == 'POST':
        data = request.form
        if all(data.values()):
            dia_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "UPDATE products SET title = ?, description = ?, photo = ?, price = ?, category_id = ?, updated = ? WHERE id = ?"
            get_db().execute(sql, (data['title'], data['description'], data['photo'], data['price'], data['category_id'], dia_actual, id))
            get_db().commit()
            return redirect(url_for('products_list'))
    abort(404)

@app.route('/products/delete/<int:id>', methods=["GET", "POST"])
def products_delete(id):
    product = obtenir_producte_id(id)
    if not product:
        abort(404)

    if request.method == 'GET':
        categories = obtenir_categories()
        return render_template('products/delete.html', results=product, categories=categories)
    elif request.method == 'POST':
        get_db().execute("DELETE FROM products WHERE id = ?", (id,))
        get_db().commit()
        return redirect(url_for('products_list'))
    abort(404)


# from flask import Flask, render_template, g, request, redirect, url_for, abort
# import sqlite3
# import datetime

# app = Flask(__name__)

# DATABASE = 'database.db'

# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = sqlite3.connect(DATABASE)
#         db.row_factory = sqlite3.Row
#     return db

# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()

# def query_db(query, args=(), one=False):
#     cur = get_db().execute(query, args)
#     rv = cur.fetchall()
#     cur.close()
#     return (rv[0] if rv else None) if one else rv

# @app.route("/")
# def hello_world():
#     return render_template('HelloWorld.html')

# @app.route('/products/list')
# def products_list():
#     products = []
#     myresult = query_db("SELECT * FROM products")
#     if myresult is None:
#         app.logger.info("No hi ha productes!!!")
#     else : 
#         for x in myresult:
#             products.append(x)
#     return render_template('products/list.html',results=products)

# @app.route('/products/read/<int:id>')
# def products_read(id):
#     categories = []
#     myresult = query_db("SELECT * FROM categories")
#     for x in myresult:
#         categories.append(x)
#     myresult = query_db("SELECT * FROM products WHERE id = ?", (id,))
#     return render_template('products/read.html',results=myresult,categories=categories)   

# @app.route('/products/create', methods=["GET", "POST"])
# def products_create():
#     if request.method == 'GET':
#         categories = []
#         myresult = query_db("SELECT * FROM categories")
#         for x in myresult:
#             categories.append(x)
#         return render_template('products/create.html', results=categories)
#     elif request.method == 'POST':
#             data = request.form
#             if data['title'] != "" and data['description'] != "" and data['photo'] != "" and data['price'] != "":
#                 mydb = get_db()
#                 mycursor = mydb.cursor()
#                 dia = datetime.datetime.now()
#                 dia_actual = dia.strftime("%Y-%m-%d %H:%M:%S")
#                 sql = "INSERT INTO products (title, description, photo, price, category_id, seller_id, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
#                 mycursor.execute(sql, (data['title'], data['description'], data['photo'], data['price'], data['category_id'], 111, dia_actual, dia_actual))
#                 mydb.commit()
#                 return redirect(url_for('products_list'))
#             else:
#                 return redirect(url_for('hello_world'))
#     else:
#         abort(404)

# @app.route('/products/update/<int:id>', methods=["GET", "POST"])
# def products_update(id):
#     if request.method == 'GET':
#         categories = []
#         myresult = query_db("SELECT * FROM categories")
#         for x in myresult:
#             categories.append(x)
#         myresult = query_db("SELECT * FROM products WHERE id = ?", (id,))
#         return render_template('products/update.html',results=myresult,categories=categories)
#     elif request.method == 'POST':
#         data = request.form
#         if data['title'] != "" and data['description'] != "" and data['photo'] != "" and data['price'] != "":
#             mydb = get_db()
#             mycursor = mydb.cursor()
#             dia = datetime.datetime.now()
#             dia_actual = dia.strftime("%Y-%m-%d %H:%M:%S")
#             sql = "UPDATE products SET title = ?, description = ?, photo = ?, price = ?, category_id = ?, updated = ? WHERE id = ?"
#             mycursor.execute(sql, (data['title'], data['description'], data['photo'], data['price'], data['category_id'], dia_actual, id))
#             mydb.commit()
#             return redirect(url_for('products_list'))
#         else:
#             return redirect(url_for('hello_world'))

# @app.route('/products/delete/<int:id>', methods=["GET", "POST"])
# def products_delete(id):
#     if request.method == 'GET':
#         categories = []
#         myresult = query_db("SELECT * FROM categories")
#         for x in myresult:
#             categories.append(x)
#         myresult = query_db("SELECT * FROM products WHERE id = ?", (id,))
#         return render_template('products/delete.html',results=myresult,categories=categories)
#     elif request.method == 'POST':
#         mydb = get_db()
#         mycursor = mydb.cursor()
#         sql = "DELETE FROM products where id = ?"
#         mycursor.execute(sql, (id,))
#         mydb.commit()
#         return redirect(url_for('products_list'))   
#     else:
#         abort(404)

# app.logger.info("--------")
# app.logger.info()
# app.logger.info("--------")
# app.logger.debug()