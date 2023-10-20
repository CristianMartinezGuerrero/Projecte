from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)


UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "xxx"

def allowed_file(photoname):
    return '.' in photoname and photoname.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

basedir = os.path.abspath(os.path.dirname(__file__)) 

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + basedir + "/database.db"
app.config["SQLALCHEMY_ECHO"] = True

# Inicio SQLAlchemy
db = SQLAlchemy()
db.init_app(app)

# Taula categories
class categories(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)

# Taula users
class users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Taula products
class products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Taula orders
class orders(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('product_id', 'buyer_id', name='uc_product_buyer'),
    )

# Taula confirmed_orders
class confirmed_orders(db.Model):
    __tablename__ = "confirmed_orders"
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route('/')
def init():
    return redirect(url_for('products_list'))

@app.route("/hello")
def hello_world():
    return render_template('HelloWorld.html')

@app.route('/products/list')
def products_list():
    try:
        products_with_categories = db.session.query(products, categories).join(categories).order_by(products.id.asc()).all()
        return render_template('products/list.html', products_with_categories=products_with_categories)
    except Exception:
        flash(f'Error al cargar la lista de productos.')
        return redirect(url_for('init'))

@app.route('/products/create', methods = ['POST', 'GET'])
def products_create():
    if request.method == 'GET':
        cat = db.session.query(categories).order_by(categories.id.asc()).all()
        return render_template('products/create.html', categories=cat)
    elif request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            photo = request.files['photo']
            price = request.form['price']
            category_id = request.form['category_id']
            seller_id = 10
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                new_product = products()
                new_product.title=title
                new_product.description=description
                new_product.photo=filename
                new_product.price=price
                new_product.category_id=category_id
                new_product.seller_id= seller_id
                new_product.created=datetime.now()
                new_product.updated=datetime.now()


                db.session.add(new_product)
                db.session.commit()
                flash('Producto creado con éxito')
                return redirect(url_for('products_list'))
        except Exception:
            flash('Error al crear el producto.')
            return redirect(url_for('products_list'))

@app.route('/products/read/<int:products_id>')
def products_read(products_id):
    (product, category) = db.session.query(products, categories).join(categories).filter(products.id == products_id).one()
    if not product:
        flash('No se encontró ningún producto con el ID proporcionado.')
        return redirect(url_for('products_list'))
    if not category:
        flash('Error al cargar las categorias.')
        return redirect(url_for('products_list'))
    return render_template('products/read.html', product = product, category = category)

@app.route('/products/update/<int:products_id>',methods = ['POST', 'GET'])
def products_update(products_id):
    pro = db.session.query(products).filter(products.id == products_id).one()
    
    if request.method == 'GET':
        cat = db.session.query(categories).order_by(categories.id.asc()).all()
        return render_template('products/update.html', product = pro, categories = cat)
    else:
        try:
            title = request.form['title']
            description = request.form['description']
            photo = request.files['photo']
            price = request.form['price']
            category_id = request.form['category_id']
            seller_id = 10
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                pro.title=title
                pro.description=description
                pro.photo=filename
                pro.price=price
                pro.category_id=category_id
                pro.seller_id= seller_id
                pro.updated=datetime.now()

                db.session.add(pro)
                db.session.commit()
                flash('Producto actualizado con éxito')
                return redirect(url_for('products_read', products_id = products_id))
        except Exception:
            flash('Error al actualizar el producto. Faltan datos obligatorios.')
            return redirect(url_for('products_list'))
        
@app.route('/products/delete/<int:products_id>',methods = ['GET', 'POST'])
def products_delete(products_id):
    (product, category) = db.session.query(products, categories).join(categories).filter(products.id == products_id).one()
    if not product:
        flash('No se encontró ningún producto con el ID proporcionado.')
        return redirect(url_for('products_list'))
    if not category:
        flash('Error al cargar las categorias.')
        return redirect(url_for('products_list'))
    if request.method == 'GET':
        return render_template('products/delete.html', product = product, category = category)
    else:
        try:
            db.session.delete(product)
            db.session.commit()
            flash('Producto eliminado con éxito')
            return redirect(url_for('products_list'))
        except Exception:
            flash(f'Error al eliminar el producto.')
            return redirect(url_for('products_list'))