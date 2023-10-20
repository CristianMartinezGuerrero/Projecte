from flask import Blueprint, redirect, url_for, render_template, request, flash, current_app
from .models import categories, products
from . import db_manager as db
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from .forms import ItemForm, DeleteForm

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
    cat = db.session.query(categories).order_by(categories.id.asc()).all()

    form = ItemForm()
    form.category_id.choices = [(categories.id, categories.name) for categories in cat]

    if form.validate_on_submit(): # si s'ha fet submit al formulari
        # he de crear un nou item
        new_item = products()
        # dades del formulari a l'objecte item
        form.populate_obj(new_item)

        # insert!
        db.session.add(new_item)
        db.session.commit()

        # https://en.wikipedia.org/wiki/Post/Redirect/Get
        return redirect(url_for('main_bp.products_list'))
    else: #GET
        return render_template('products/create.html', form = form)


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
    cat = db.session.query(categories).order_by(categories.id.asc()).all()

    form = ItemForm(obj = pro)
    form.category_id.choices = [(categories.id, categories.name) for categories in cat]

    if form.validate_on_submit(): # si s'ha fet submit al formulari
        # dades del formulari a l'objecte item
        form.populate_obj(pro)

        # update!
        db.session.add(pro)
        db.session.commit()

        return redirect(url_for('main_bp.products_read', products_id = products_id))
    else: #GET
        return render_template('products/update.html', product = pro, categories = cat, form = form)

@main_bp.route('/products/delete/<int:products_id>',methods = ['GET', 'POST'])
def products_delete(products_id):
    (product, category) = db.session.query(products, categories).join(categories).filter(products.id == products_id).one()
    
    form = DeleteForm()
    if form.validate_on_submit(): # si s'ha fet submit al formulari
        # delete!
        db.session.delete(product)
        db.session.commit()

        return redirect(url_for('main_bp.products_list'))
    else: # GET
        return render_template('products/delete.html', product = product, category = category, form = form)