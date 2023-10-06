from flask import Flask, render_template, request, redirect, url_for, abort, g, flash
import sqlite3, datetime, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
DATABASE = 'database.db'
app.secret_key = 'xxx'
app.config['UPLOAD_FOLDER'] = 'uploads'

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
    try:
        products = query_db("SELECT * FROM products")
        return render_template('products/list.html', results=products)
    except Exception as e:
        flash(f'Error al cargar el listado de productos: {str(e)}')
        return redirect(url_for('hello_world'))

@app.route('/products/read/<int:id>')
def products_read(id):
    product = obtenir_producte_id(id)
    if not product:
        flash('No se encontró ningún producto con el ID proporcionado.')
        return redirect(url_for('products_list'))
    categories = obtenir_categories()
    if not categories:
        flash('Error al cargar las categorias.')
        return redirect(url_for('products_list'))
    return render_template('products/read.html', results=product, categories=categories)

@app.route('/products/create', methods=["GET", "POST"])
def products_create():
    if request.method == 'GET':
        categories = obtenir_categories()
        if not categories:
            flash('Error al cargar las categorias.')
            return redirect(url_for('products_list'))
        return render_template('products/create.html', results=categories)
    elif request.method == 'POST':
        data = request.form
        if all(data.values()) and len(data['title']) <= 255:
            photo = request.files['photo']
            if len(photo.read()) <= 2 * 1024 * 1024:
                filename = secure_filename(photo.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(file_path)
                app.logger.info("--------")
                app.logger.info(filename)
                app.logger.info("--------")
                mydb = get_db()
                mycursor = mydb.cursor()
                dia_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql = "INSERT INTO products (title, description, photo, price, category_id, seller_id, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                mycursor.execute(sql, (data['title'], data['description'], filename, data['price'], data['category_id'], 10, dia_actual, dia_actual))
                mydb.commit()
                flash('Producto creado con éxito')
                return redirect(url_for('products_list'))
            else:
                flash('Error al crear el producto. La imagen debe ser menor de 2 MB.')
                return redirect(url_for('products_list'))
        else:
            flash('Error al crear el producto. Faltan datos obligatorios o el título excede los 255 caracteres.')
            return redirect(url_for('products_list'))

@app.route('/products/update/<int:id>', methods=["GET", "POST"])
def products_update(id):
    product = obtenir_producte_id(id)
    if not product:
        flash('El producto que intentas actualizar no existe.')
        return redirect(url_for('products_list'))
    
    if request.method == 'GET':
        categories = obtenir_categories()
        if not categories:
            flash('Error al cargar las categorias.')
            return redirect(url_for('products_list'))
        return render_template('products/update.html', results=product, categories=categories)
    elif request.method == 'POST':
        data = request.form
        if all(data.values()):
            dia_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "UPDATE products SET title = ?, description = ?, photo = ?, price = ?, category_id = ?, updated = ? WHERE id = ?"
            get_db().execute(sql, (data['title'], data['description'], data['photo'], data['price'], data['category_id'], dia_actual, id))
            get_db().commit()
            flash('Producto actualizado con éxito')
            return redirect(url_for('products_list'))
        else:
            flash('Error al actualizar el producto. Faltan datos obligatorios.')
            return redirect(url_for('products_list'))        

@app.route('/products/delete/<int:id>', methods=["GET", "POST"])
def products_delete(id):
    product = obtenir_producte_id(id)
    if not product:
        flash('El producto que intentas eliminar no existe.')
        return redirect(url_for('products_list'))

    if request.method == 'GET':
        categories = obtenir_categories()
        if not categories:
            flash('Error al cargar las categorias.')
            return redirect(url_for('products_list'))
        return render_template('products/delete.html', results=product, categories=categories)
    elif request.method == 'POST':
        get_db().execute("DELETE FROM products WHERE id = ?", (id,))
        get_db().commit()
        flash('Producto eliminado con éxito')
        return redirect(url_for('products_list'))