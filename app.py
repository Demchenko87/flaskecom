import re

from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore, Security, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditor, CKEditorField
from wtforms import StringField, IntegerField, TextAreaField, HiddenField, SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
import random
import email_validator
app = Flask(__name__)
ckeditor = CKEditor(app)
photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/images'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trendy.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'mysecret'
# -- security
app.config['SECURITY_PASSWORD_SALT'] = 'salt'
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
configure_uploads(app, photos)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    price = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    slug = db.Column(db.String(140), unique=True)
    description = db.Column(db.String(500))
    image = db.Column(db.String(100), nullable=True)
    image2 = db.Column(db.String(100), nullable=True)
    image3 = db.Column(db.String(100), nullable=True)
    image4 = db.Column(db.String(100), nullable=True)
    order = db.relationship('Order_Item', backref='product', lazy=True)

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.name:
            self.slug = slugify(self.name)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(5))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    phone_number = db.Column(db.Integer)
    email = db.Column(db.String(50))
    address = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(20))
    country = db.Column(db.String(20))
    status = db.Column(db.String(10))
    payment_type = db.Column(db.String(10))
    items = db.relationship('Order_Item', backref='order', lazy=True)

    def order_total(self):
        ship_price = Shipping.query.first()
        shipping = ship_price.price

        return db.session.query(db.func.sum(Order_Item.quantity * Product.price)).join(Product).filter(Order_Item.order_id == self.id).scalar() + shipping

    def quantity_total(self):
        return db.session.query(db.func.sum(Order_Item.quantity)).filter(Order_Item.order_id == self.id).scalar()

class Order_Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)

class AddProduct(FlaskForm):
    name = StringField('Name')
    price = IntegerField('Price')
    stock = IntegerField('Stock')
    description = CKEditorField('Description')
    slug = StringField('Slug')
    image = FileField('Image', validators=[FileAllowed(IMAGES, 'Only images are accepted.')])
    image2 = FileField('Image', validators=[FileAllowed(IMAGES, 'Only images are accepted.')])
    image3 = FileField('Image', validators=[FileAllowed(IMAGES, 'Only images are accepted.')])
    image4 = FileField('Image', validators=[FileAllowed(IMAGES, 'Only images are accepted.')])


class AddToCart(FlaskForm):
    quantity = IntegerField('Quantity')
    id = HiddenField('ID')

class Checkout(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone_number = StringField('Numb er')
    email = StringField('Email')
    address = StringField('Address')
    city = StringField('City')
    delivery = SelectField('Delivery', choices=[('Самовывоз', 'Самовывоз'),('Новая почта', 'Новая почта'), ('Укрпочта', 'Укрпочта'), ('Мист Экспресс', 'Мист Экспресс'), ('Интайм', 'Интайм'), ('Деливери', 'Деливери'), ('Автолюкс', 'Автолюкс'), ('Zruchna', 'Zruchna'), ('Делфаст', 'Делфаст')])
    branch = StringField('Branch')
    payment_type = SelectField('Payment Type', choices=[('Картой', 'Картой'), ('Наличными при получении', 'Наличными при получении'), ('Наложенный платеж', 'Наложенный платеж')])
    items = db.relationship('Order_Item', backref='order', lazy=True)

# ---- Flask Security
roles_users = db.Table('roles_users', db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                       )
#----- end flask security

#---Create User and Role user
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
#----end Create User and Role user

#---- Shipping
class Shipping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
#
# class AddShipping(FlaskForm):
#     price = IntegerField('Price')
#---- End Shipping

class Slider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pagetitle = db.Column(db.String(100))
    description = db.Column(db.String(100))
    image = db.Column(db.String(100))

class AddSlider(FlaskForm):
    pagetitle = StringField('Заголовок')
    description = CKEditorField('Описание')
    image = FileField('Image', validators=[FileAllowed(IMAGES, 'Only images are accepted.')])

def handle_cart():
    products = []
    grand_total = 0
    ship_price = Shipping.query.first()
    shipping = ship_price.price
    index = 0
    quatity_total = 0
    for item in session['cart']:
        product = Product.query.filter_by(id=item['id']).first()
        quantity = int(item['quantity'])
        quatity_total += quantity
        total = quantity * product.price
        grand_total += total
        products.append({'id': product.id, 'name': product.name, 'price':  product.price, 'image': product.image, 'quantity': quantity, 'total': total, 'index': index})
        index += 1
    grand_total_plus_shipping = grand_total + shipping
    return products, grand_total, grand_total_plus_shipping, shipping, quatity_total

@app.route('/')
def index():
    # session['cart'] = []

    slider = Slider.query.all()
    count_cart = check_count()
    products = Product.query.order_by(Product.name.desc())
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    pages = products.paginate(page=page, per_page=2)
    return render_template('index.html', pages=pages, products=products, count_cart=count_cart, slider=slider)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/search', methods=['GET', 'POST'])
def search():
    count_cart = check_count()
    search = request.args.get('search')
    if search:
        products = Product.query.filter(Product.name.contains(search) | Product.description.contains(search))
    else:
        products = Product.query.all()
    return render_template('search.html', products=products, count_cart=count_cart)

@app.route('/product/<id>')
def product(id):
    product = Product.query.filter_by(id=id).first()
    form = AddToCart()
    count_cart = check_count()
    return render_template('view-product.html', product=product, form=form, count_cart=count_cart)

# @app.route('/quick-add/<id>')
# def quick_add(id):
#     if 'cart' not in session:
#         session['cart'] = []
#     session['cart'].append({'id': id, 'quantity': 1})
#     session.modified = True
#     return redirect(url_for('index'))

#----json add
@app.route('/quick-add-json', methods=['POST'])
def quick_add():
    id = request.form['id_tov']
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append({'id': id, 'quantity': 1})
    session.modified = True
    count = 0
    for i in session['cart']:
        count += 1
    return jsonify({'id': id, 'count': count})


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []
    form = AddToCart()
    if form.validate_on_submit():
        session['cart'].append({'id': form.id.data, 'quantity': form.quantity.data})
        session.modified = True
    return redirect(request.referrer)

@app.route('/cart')
def cart():
    count_cart = check_count()
    products, grand_total, grand_total_plus_shipping, shipping, quatity_total = handle_cart()
    return render_template('cart.html', count_cart=count_cart, products=products, shipping=shipping, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quatity_total=quatity_total)

@app.route('/remove-from-cart/<index>')
def remove_form_cart(index):
    del session['cart'][int(index)]
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = Checkout()
    products, grand_total, grand_total_plus_shipping, shipping, quatity_total = handle_cart()
    count_cart = check_count()
    if form.validate_on_submit():
        order = Order()
        form.populate_obj(order)
        order.reference = ''.join([random.choice('ABCDE') for _ in range(5)])
        order.status = 'Новый заказ'
        for product in products:
            order_item = Order_Item(quantity=product['quantity'], product_id=product['id'])
            order.items.append(order_item)
            product = Product.query.filter_by(id=product['id']).update({'stock': Product.stock - product['quantity']})
        db.session.add(order)
        db.session.commit()
        session['cart'] = []
        session.modified = True
        return redirect(url_for('index'))
    return render_template('checkout.html', form=form, products=products, shipping=shipping, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, count_cart=count_cart, quatity_total=quatity_total)

@app.route('/admin')
@login_required
def admin():
    products = Product.query.all()
    products_in_stock = Product.query.filter(Product.stock > 0).count()
    orders = Order.query.all()
    count_cart = check_count()
    return render_template('admin/index.html', admin=True, count_cart=count_cart, products=products, products_in_stock=products_in_stock, orders=orders)

@app.route('/statistic')
@login_required
def statistic():
    orders_done = Order.query.filter_by(status='Выполнен').count()
    orders_new = Order.query.filter_by(status='Новый заказ').count()
    orders_pay = Order.query.filter_by(status='Оплачен').count()
    orders_send = Order.query.filter_by(status='Отправлен').count()
    orders_cancel = Order.query.filter_by(status='Отменен').count()

    return render_template('admin/statistic.html', admin=True, orders_done=orders_done, orders_new=orders_new, orders_pay=orders_pay, orders_send=orders_send, orders_cancel=orders_cancel)


@app.route('/admin/list-products')
@login_required
def list_products():
    products = Product.query.all()
    products_in_stock = Product.query.filter(Product.stock > 0).count()
    orders = Order.query.all()
    count_cart = check_count()
    return render_template('admin/list_products.html', admin=True, count_cart=count_cart, products=products, products_in_stock=products_in_stock, orders=orders)

# @app.route('/admin/add_shipping', methods=['GET', 'POST'])
# @login_required
# def add_shipping():
#     form = AddShipping()
#     if form.validate_on_submit():
#         new_product = Shipping(price=form.price.data)
#         db.session.add(new_product)
#         db.session.commit()
#         return redirect(url_for('admin'))
#     return render_template('admin/add_shipping.html', admin=True, form=form)

@app.route('/admin/edit_shipping', methods=['GET', 'POST'])
@login_required
def edit_shipping():
    shipping = Shipping.query.first()
    if request.method == 'POST':
        shipping.price = request.form['price']
        db.session.commit()
        return redirect(request.referrer)
    return render_template('admin/edit_shipping.html', admin=True, shipping=shipping)

@app.route('/admin/add_slider', methods=['GET', 'POST'])
@login_required
def add_slider():
    form = AddSlider()
    slider = Slider.query.all()
    if form.validate_on_submit():
        image_url_main = photos.save(form.image.data)
        image_url = 'images/' + image_url_main
        new_slider = Slider(pagetitle=form.pagetitle.data, description=form.description.data, image=image_url)
        db.session.add(new_slider)
        db.session.commit()
        return redirect(url_for('add_slider'))
    return render_template('admin/add_slider.html', admin=True, form=form, slider=slider)

@app.route('/admin/edit_slider/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_slider(id):
    slider = Slider.query.get(id)
    if request.method == 'POST':
        slider.pagetitle = request.form['pagetitle']
        slider.description = request.form['description']

        if request.files['image'].filename == '':
            pass
        else:
            image_url_main = photos.save(request.files["image"])
            slider.image = 'images/' + image_url_main
        try:
            db.session.commit()
            return redirect(request.referrer)
        except:
            return "При редактировании произошла ошибка"
    else:
        return render_template('admin/edit_slider.html', admin=True, slider=slider)

@app.route('/admin/delete/slider/<int:id>', methods=['GET'])
@login_required
def delete_slider(id):
    slider = Slider.query.filter_by(id=id).first()
    db.session.delete(slider)
    db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/delete/<int:id>', methods=['GET'])
@login_required
def remove_product(id):
    event = Product.query.filter_by(id=id).first()
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('list_products'))

@app.route('/admin/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_product(id):
    product = Product.query.get(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.stock = request.form['stock']
        product.description = request.form['description']
        if request.files['image'].filename == '':
            pass
        else:
            image_url_main = photos.save(request.files["image"])
            product.image = 'images/' + image_url_main

        if request.files['image2'].filename == '':
            pass
        else:
            image_url2 = photos.save(request.files["image2"])
            product.image2 = 'images/' + image_url2

        if request.files['image3'].filename == '':
            pass
        else:
            image_url3 = photos.save(request.files["image3"])
            product.image3 = 'images/' + image_url3

        if request.files['image4'].filename == '':
            pass
        else:
            image_url4 = photos.save(request.files["image4"])
            product.image4 = 'images/' + image_url4

        try:
            db.session.commit()
            return redirect('/admin/list-products')
        except:
            return "При редактировании произошла ошибка"
    else:
        return render_template('admin/edit-product.html', product=product, admin=True)

@app.route('/admin/delete_order/<int:id>', methods=['GET'])
@login_required
def remove_order(id):
    event = Order.query.filter_by(id=id).first()
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddProduct()
    if form.validate_on_submit():
        if form.image.data is None:
            image_url = ''
        else:
            image_url_main = photos.save(form.image.data)
            image_url = 'images/' + image_url_main

        if form.image2.data is None:
            image_url2 = ''
        else:
            image_url_2 = photos.save(form.image2.data)
            image_url2 = 'images/' + image_url_2

        if form.image3.data is None:
            image_url3 = ''
        else:
            image_url_3 = photos.save(form.image3.data)
            image_url3 = 'images/' + image_url_3

        if form.image4.data is None:
            image_url4 = ''
        else:
            image_url_4 = photos.save(form.image4.data)
            image_url4 = 'images/' + image_url_4

        new_product = Product(name=form.name.data, slug=form.slug.data, price=form.price.data, stock=form.stock.data, description=form.description.data, image=image_url, image2=image_url2, image3=image_url3, image4=image_url4)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('list_products'))

    return render_template('admin/add-product.html', admin=True, form=form)

@app.route('/admin/order/<order_id>', methods=['GET', 'POST'])
@login_required
def order(order_id):
    ship_price = Shipping.query.first()
    shipping = ship_price.price
    order = Order.query.filter_by(id=int(order_id)).first()
    if request.method == 'POST':
        order.status = request.form['status']
        db.session.commit()
    return render_template('admin/view-order.html', order=order, shipping=shipping, admin=True)


@app.route('/admin/edit/order/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_order(id):
    order = Order.query.get(id)
    count_cart = check_count()
    if request.method == 'POST':
        order.first_name = request.form['first_name']
        order.last_name = request.form['last_name']
        order.phone_number = request.form['phone_number']
        order.email = request.form['email']
        order.address = request.form['address']
        order.city = request.form['city']
        order.payment_type = request.form['payment_type']
        db.session.commit()
    return render_template('admin/edit-order.html', admin=True, order=order, count_cart=count_cart)

def check_count():
    count_cart = 0
    if 'cart' in session:
        for item in session['cart']:
            quantity = int(item['quantity'])
            count_cart += quantity
    else:
        count_cart = 0
    return count_cart

if __name__ == '__main__':
    app.run()
