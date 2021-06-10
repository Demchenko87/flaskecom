from flask import Flask, flash, render_template, redirect, url_for, session, request, jsonify
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore, Security, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, HiddenField, SelectField
from flask_wtf.file import FileField, FileAllowed
import random
import email_validator
app = Flask(__name__)

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

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    price = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    description = db.Column(db.String(500))
    image = db.Column(db.String(100))
    order = db.relationship('Order_Item', backref='product', lazy=True)

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
        shipping = 30
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
    description = TextAreaField('Description')
    image = FileField('Image', validators=[FileAllowed(IMAGES, 'Only images are accepted.')])

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
    state = SelectField('State', choices=[('CA', 'California'), ('WA', 'Washington'), ('NV', 'Nevada')])
    country = SelectField('Country', choices=[('US', 'United States'), ('UK', 'United Kindom'), ('FRA', 'France')])
    payment_type = SelectField('Payment Type', choices=[('VI', 'VISA'), ('MA', 'MasteCard'), ('PA', 'PayPal')])
    items = db.relationship('Order_Item', backref='order', lazy=True)

# ---- Flask Security
roles_users = db.Table('roles_users', db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                       )

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


def handle_cart():
    products = []
    grand_total = 0
    shipping = 30
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
    products = Product.query.all()
    count_cart = check_count()
    return render_template('index.html', products=products, count_cart=count_cart)

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
    print(session['cart'])
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

    return redirect(url_for('index'))


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
        order.status = 'PENDING'
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


@app.route('/admin/delete/<int:id>', methods=['GET'])
@login_required
def remove_product(id):
    event = Product.query.filter_by(id=id).first()
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('admin'))

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
        image_url_main = photos.save(form.image.data)
        image_url = 'images/' + image_url_main
        print(image_url)
        new_product = Product(name=form.name.data, price=form.price.data, stock=form.stock.data, description=form.description.data, image=image_url)

        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('admin'))

    return render_template('admin/add-product.html', admin=True, form=form)

@app.route('/admin/order/<order_id>')
@login_required
def order(order_id):
    order = Order.query.filter_by(id=int(order_id)).first()
    shipping = 30
    return render_template('admin/view-order.html', order=order, shipping=shipping, admin=True)

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
