from flask import Blueprint, redirect, url_for, render_template, request, flash, current_app
from .models import categories, products
from . import db_manager as db
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# Blueprint
main_bp = Blueprint(
    "main_bp", __name__, template_folder="templates", static_folder="static/css"
)
ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg'}
upload_folder = current_app.config['UPLOAD_FOLDER']

def allowed_file(photoname):
    return '.' in photoname and photoname.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def init():
    return redirect(url_for('main_bp.products_list'))

@main_bp.route("/hello")
def hello_world():
    return render_template('HelloWorld.html')

@main_bp.route('/products/list')
def products_list():
    try:
        products_with_categories = db.session.query(products, categories).join(categories).order_by(products.id.asc()).all()
        return render_template('products/list.html', products_with_categories=products_with_categories)
    except Exception:
        flash(f'Error al cargar la lista de productos.')
        return redirect(url_for('main_bp.init'))

@main_bp.route('/products/create', methods = ['POST', 'GET'])
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
                file_path = os.path.join(upload_folder, filename)
                photo.save(file_path)

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
                return redirect(url_for('main_bp.products_list'))
        except Exception:
            flash('Error al crear el producto.')
            return redirect(url_for('main_bp.products_list'))

@main_bp.route('/products/read/<int:products_id>')
def products_read(products_id):
    (product, category) = db.session.query(products, categories).join(categories).filter(products.id == products_id).one()
    if not product:
        flash('No se encontró ningún producto con el ID proporcionado.')
        return redirect(url_for('main_bp.products_list'))
    if not category:
        flash('Error al cargar las categorias.')
        return redirect(url_for('main_bp.products_list'))
    return render_template('products/read.html', product = product, category = category)

@main_bp.route('/products/update/<int:products_id>',methods = ['POST', 'GET'])
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
            if allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                file_path = os.path.join(upload_folder, filename)
                photo.save(file_path)
            if photo:
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
                return redirect(url_for('main_bp.products_read', products_id = products_id))
        except Exception:
            flash('Error al actualizar el producto. Faltan datos obligatorios.')
            return redirect(url_for('main_bp.products_list'))
        
@main_bp.route('/products/delete/<int:products_id>',methods = ['GET', 'POST'])
def products_delete(products_id):
    (product, category) = db.session.query(products, categories).join(categories).filter(products.id == products_id).one()
    if not product:
        flash('No se encontró ningún producto con el ID proporcionado.')
        return redirect(url_for('main_bp.products_list'))
    if not category:
        flash('Error al cargar las categorias.')
        return redirect(url_for('main_bp.products_list'))
    if request.method == 'GET':
        return render_template('products/delete.html', product = product, category = category)
    else:
        try:
            db.session.delete(product)
            db.session.commit()
            flash('Producto eliminado con éxito')
            return redirect(url_for('main_bp.products_list'))
        except Exception:
            flash(f'Error al eliminar el producto.')
            return redirect(url_for('main_bp.products_list'))