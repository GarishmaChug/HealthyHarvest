from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app and configure database
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db")
db = SQLAlchemy(app)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Ensure this key is set properly

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")  # Default role

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product', backref='cart_items')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(150), nullable=True)

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}')"

# Create database tables
# with app.app_context():
  
#     db.create_all()
def add_admin_user():
    admin_user = User.query.filter_by(email='admin@example.com').first()
    if not admin_user:
        hashed_password = generate_password_hash('adminpassword', method='pbkdf2:sha256')
        new_admin = User(username='admin', email='admin@example.com', password=hashed_password, role='admin')
        db.session.add(new_admin)
        db.session.commit()
        print("Admin user added to the database.")

with app.app_context():
   
    db.create_all()  # Create tables again
    add_admin_user()  # Add admin user
   
    
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/admin/products', methods=['GET'])
def admin_products():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    products = Product.query.all()
    return render_template('admin_products.html', products=products)

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.image = request.form['image']
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))

    return render_template('edit_products.html', product=product)

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please log in to proceed to checkout.', 'warning')
        return redirect(url_for('login'))

    # Clear the cart from the database
    Cart.query.filter_by(user_id=session['user_id']).delete()
    db.session.commit()

    # Redirect to the actual checkout page
    return redirect(url_for('checkout_page'))

@app.route('/checkout_page')
def checkout_page():
    if 'user_id' not in session:
        flash('Please log in to view the checkout page.', 'warning')
        return redirect(url_for('login'))

    return render_template('checkout.html')  

def add_beauty_products():
    beauty_products = [
        {'name': 'Sol de Janeiro Beija Flor Jet Set', 'price': '$32', 'image': 'static/images/product1.webp'},
        {'name': 'Charlotte Tilbury Beauty Pillow Talk Mini Pillow Talk lipstick and more', 'price': '$25', 'image': 'static/images/product2.webp'},
        {'name': 'Sol de Janeiro Bom Dia Bright Jet set', 'price': '$33', 'image': 'static/images/product3.jpg'},
        {'name': 'Glow Recipe Fruit Babies Bestsellers Kit', 'price': '$250', 'image': 'static/images/product4.jpeg'},
        {'name': 'Fenty Beauty Pro Filtr Soft Matte Longwear Foundation', 'price': '$38', 'image': 'static/images/product5.jpeg'},
        {'name': 'Urban Decay Naked3 Eyeshadow Palette', 'price': '$54', 'image': 'static/images/product6.jpeg'},
        {'name': 'Anastasia Beverly Hills Brow Wiz', 'price': '$21', 'image': 'static/images/product7.jpeg'},
        {'name': 'Too Faced Better Mascara', 'price': '$25', 'image': 'static/images/product8.jpeg'},
        {'name': 'MAC Cosmetics Matte Lipstick', 'price': '$19', 'image': 'static/images/product9.jpeg'},
        {'name': 'Tarte Shape Tape Concealer', 'price': '$27', 'image': 'static/images/product10.jpeg'},
        {'name': 'Maybelline Fit Me Matte + Poreless Foundation', 'price': '$10', 'image': 'static/images/product11.jpeg'},
        {'name': 'Huda Beauty Desert Dusk Palette', 'price': '$65', 'image': 'static/images/product12.jpeg'},
        {'name': 'NARS Radiant Creamy Concealer', 'price': '$30', 'image': 'static/images/product13.jpeg'},
        {'name': 'Fenty Beauty Killawatt Freestyle Highlighter', 'price': '$36', 'image': 'static/images/product14.jpeg'},
        {'name': 'L`Oréal Paris Voluminous Lash Paradise Mascara', 'price': '$12', 'image': 'static/images/product15.jpeg'},
        {'name': 'Benefit Cosmetics Hoola Matte Bronzer', 'price': '$30', 'image': 'static/images/product16.jpeg'},
        {'name': 'Charlotte Tilbury Airbrush Flawless Finish Powder', 'price': '$45', 'image': 'static/images/product17.jpeg'},
        {'name': 'Becca Shimmering Skin Perfector Pressed Highlighter', 'price': '$38', 'image': 'static/images/product18.jpeg'},
        {'name': 'IT Cosmetics Your Skin But Better CC+ Cream', 'price': '$39', 'image': 'static/images/product19.jpeg'},
        {'name': 'Tatcha The Dewy Skin Cream', 'price': '$68', 'image': 'static/images/product20.jpeg'},
    ]

    for product in beauty_products:
        new_product = Product(name=product['name'], price=product['price'], image=product['image'])
        db.session.add(new_product)

        db.session.commit()
    print("Beauty products added to the database.")


with app.app_context():
    # db.drop_all()  # Drop all tables (use with caution)
    db.create_all()  # Create tables again
    add_beauty_products()  # Add beauty products after recreating the tables
@app.route("/beauty")
def beauty():
    products = Product.query.all()  # Fetch all products from the database
    return render_template('beauty.html', products=products)

@app.route('/product')
def products():
    products_list = [
        {"name": "Pain Reliever Tablet", "price": "$12.99", "expiry": "12/2026", "image": "static/images/painrelif.jpg"},
        {"name": "Cough Syrup", "price": "$8.50", "expiry": "03/2025", "image": "static/images/cough.jpg"},
        {"name": "Multivitamin Capsules", "price": "$15.75", "expiry": "11/2027", "image": "static/images/multivitamin.jpg"},
        {"name": "Antibiotic Ointment", "price": "$5.99", "expiry": "08/2024", "image": "static/images/onitment.jpg"},
        {"name": "Cold Relief Capsules", "price": "$10.30", "expiry": "06/2025", "image": "static/images/cold.jpg"},
        {"name": "Allergy Relief Tablets", "price": "$7.99", "expiry": "09/2025", "image": "static/images/allergy.jpg"},
        {"name": "Digestive Aid Tablets", "price": "$6.50", "expiry": "07/2026", "image": "static/images/digestive.jpg"},
        {"name": "Vitamin D3 Supplement", "price": "$9.00", "expiry": "04/2027", "image": "static/images/vitamind33.jpg"},
        {"name": "Antacid Tablets", "price": "$3.75", "expiry": "01/2025", "image": "static/images/amtacid.jpg"},
        {"name": "Headache Relief Gel", "price": "$4.99", "expiry": "05/2026", "image": "static/images/haedache.jpg"},
        {"name": "Hair Growth Shampoo", "price": "$12.00", "expiry": "02/2027", "image": "static/images/hair.jpg"},
        {"name": "Sleep Aid Tablets", "price": "$8.40", "expiry": "12/2025", "image": "static/images/sleep.jpg"},
        {"name": "Band-Aids", "price": "$2.99", "expiry": "10/2026", "image": "static/images/bandaid.jpg"},
        {"name": "Eye Drops", "price": "$5.50", "expiry": "01/2025", "image": "static/images/eyedrops.jpg"},
        {"name": "Muscle Relief Cream", "price": "$7.25", "expiry": "08/2025", "image": "static/images/muscle.jpg"},
        {"name": "Moisturizing Lotion", "price": "$6.80", "expiry": "03/2025", "image": "static/images/moisturizing.jpg"},
        {"name": "Thermometer", "price": "$15.99", "expiry": "06/2027", "image": "static/images/allergy.jpg"},
        {"name": "Sunscreen Lotion", "price": "$12.99", "expiry": "09/2026", "image": "static/images/sunscreen.jpg"},
        {"name": "First Aid Kit", "price": "$25.00", "expiry": "07/2027", "image": "static/images/firstaid.jpg"},
        {"name": "Cold Compress", "price": "$8.50", "expiry": "11/2026", "image": "static/images/compress.jpg"}
    ]
    return render_template('pharmacy.html', products=products_list)

@app.route('/fruits&veg')
def fruits():
    products_list = [
        {'name': 'Apple', 'image': 'apple.png', 'price': '₹130 per each'},
        {'name': 'Banana', 'image': 'banana.png', 'price': '₹44 per kg'},
        {'name': 'Mango', 'image': 'mango.png', 'price': '₹100 per kg'},
        {'name': 'Orange', 'image': 'orange.png', 'price': '₹65 per kg each'},
        {'name': 'Litchi', 'image': 'litchi.png', 'price': '₹100 per kg'},
        {'name': 'Kiwi', 'image': 'kiwi.png', 'price': '₹123 (3 pieces)'},
        {'name': 'DragonFruit', 'image': 'dragonfruit.png', 'price': '₹63 each'},
        {'name': 'Pineapple', 'image': 'pineapple.png', 'price': '₹93 each'},
        {'name': 'Strawberry', 'image': 'strawberry.png', 'price': '₹96 (1 pack)'},
        {'name': 'Grapes', 'image': 'grapes.png', 'price': '₹70 (500g)'},
        {'name': 'Carrot', 'image': 'carrot.png', 'price': '₹20 per kg'},
        {'name': 'Pomegranate', 'image': 'pomegranet.png', 'price': '₹115 (500g)'},
        {'name': 'Watermelon', 'image': 'watermelon.png', 'price': '₹35 each'},
        {'name': 'Muskmelon', 'image': 'muskmelon.png', 'price': '₹67 each'},
        {'name': 'Papaya', 'image': 'papaya.png', 'price': '₹111 per kg'},
        {'name': 'Guava', 'image': 'guava.png', 'price': '₹120 per kg'},
        {'name': 'Potato', 'image': 'potato.png', 'price': '₹30 per kg'},
        {'name': 'Tomato', 'image': 'tomato.png', 'price': '₹40 per kg'},
        {'name': 'Green Chilli', 'image': 'greenChilli.png', 'price': '₹14 (100g)'},
        {'name': 'Cauliflower', 'image': 'cauliflower.png', 'price': '₹15 each'},
        {'name': 'Ginger', 'image': 'ginger.png', 'price': '₹23 (100g)'},
        {'name': 'Capsicum', 'image': 'capsicum.png', 'price': '₹80 per kg'},
        {'name': 'Mushroom', 'image': 'mushroom.png', 'price': '₹50 (200g)'},
        {'name': 'Garlic', 'image': 'garlic.png', 'price': '₹85 (200g)'},
        {'name': 'Cucumber', 'image': 'cucumber.png', 'price': '₹30 per kg'},
        {'name': 'Beans', 'image': 'beans.png', 'price': '₹29 (200g)'},
        {'name': 'Raddish', 'image': 'raddish.png', 'price': '₹30 per kg'},
        {'name': 'Lemon', 'image': 'lemon.png', 'price': '₹30 (220g)'},
        {'name': 'Broccoli', 'image': 'broccoli.png', 'price': '₹25 (300g)'},
        {'name': 'Onion', 'image': 'onion.png', 'price': '₹50 per kg'},
    ]
    return render_template('fruits&veg.html', products=products_list)

@app.route('/snacks')
def snacks():
    products_list = [
        {'name': 'Maggi', 'image': 'maggi.png', 'price': '₹10 per each'},
        {'name': 'Tedhe Medhe', 'image': 'TedheMedhe.png', 'price': '₹10 per each'},
        {'name': "Lay's India's Magic Masala", 'image': 'BlueLays.png', 'price': '₹10 per each'},
        {'name': "Lay's Classic Salted", 'image': 'YellowLays.png', 'price': '₹10 per each'},
        {'name': "Lay's American Style Cream & Onion", 'image': 'greenLays.png', 'price': '₹10 per each'},
        {'name': "Maggi Cheese Macroni Instant Pasta", 'image': 'cheese.png', 'price': '₹35 per each'},
        {'name': "Maggi Masala Penne Instant Pasta", 'image': 'masala.png', 'price': '₹35 per each'},
        {'name': "Oreo", 'image': 'oreo.png', 'price': '₹10 per each'},
        {'name': "Dark Fantasy", 'image': 'DarkFantasy.png', 'price': '₹30'},
        {'name': "Hide & Seek", 'image': 'Hide.png', 'price': '₹30 per each'},
        {'name': "Jim Jam", 'image': 'JimJam.png', 'price': '₹10 per each'},
        {'name': "Good Day", 'image': 'Gooday.png', 'price': '₹10 per each'},
        {'name': "Little Hearts", 'image': 'Hearts.png', 'price': '₹10 per each'},
        {'name': "Ferrero Rocher", 'image': 'Ferrero.png', 'price': '₹763 (24 pieces)'},
        {'name': "Dairy Milk Silk Fruit & Nut", 'image': 'FruitNut.png', 'price': '₹186'},
        {'name': "Kit Kat", 'image': 'Kitkat.png', 'price': '₹110'},
        {'name': "Crispello", 'image': 'crispello.png', 'price': '₹40'},
        {'name': "Munch", 'image': 'Munch.png', 'price': '₹57'},
        {'name': "ThumsUp", 'image': 'ThumsUp.png', 'price': '₹40 (750ml)'},
        {'name': "Choco Latte", 'image': 'ChocoLatte.png', 'price': '₹120'},
        {'name': "Cold Coffee", 'image': 'ColdCoffee.png', 'price': '₹120'},
        {'name': "Diet Coke", 'image': 'diet.png', 'price': '₹40 (300ml)'},
        {'name': "Fanta", 'image': 'fanta.png', 'price': '₹40 (750ml)'},
        {'name': "Sprite", 'image': 'sprite.png', 'price': '₹40 (750ml)'},
        {'name': "Limca", 'image': 'limca.png', 'price': '₹40 (750ml)'},
        {'name': "Maza", 'image': 'maza.png', 'price': '₹40 (600ml)'},
        {'name': "Mountain Dew", 'image': 'dew.png', 'price': '₹86 (2 X 750ml)'},
        {'name': "Aloo Bhujia", 'image': 'bhujia.png', 'price': '₹221 per kg'},
        {'name': "Kinder Joy", 'image': 'joy.png', 'price': '₹48'},
        {'name': "Makhana", 'image': 'makhana.png', 'price': '₹160 (100g)'},
    ]
    return render_template('snacks.html', products=products_list)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('Please log in to add items to your cart.', 'warning')
        return redirect(url_for('login'))

    existing_cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()

    if existing_cart_item:
        existing_cart_item.quantity += 1 
    else:
        new_cart_item = Cart(user_id=session['user_id'], product_id=product_id)
        db.session.add(new_cart_item)

    db.session.commit()
    flash('Item added to cart!', 'success')
    return redirect(request.referrer)

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Please log in to view your cart.', 'warning')
        return redirect(url_for('login'))

    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    return render_template('cart.html', cart_items=cart_items)

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    cart_item = Cart.query.get(item_id)
    if cart_item and cart_item.user_id == session['user_id']:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from your cart.', 'success')
    else:
        flash('Item not found in your cart.', 'error')

    return redirect(url_for('cart'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        if confirm_password != password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=session['username'], role=session['role'])
fruits_vegetables_dict = [
    {'name': 'Apple', 'image': 'apple.png', 'price': '₹130 per each'},
    {'name': 'Banana', 'image': 'banana.png', 'price': '₹44 per kg'},
    {'name': 'Mango', 'image': 'mango.png', 'price': '₹100 per kg'},
    {'name': 'Orange', 'image': 'orange.png', 'price': '₹65 per kg each'},
    {'name': 'Litchi', 'image': 'litchi.png', 'price': '₹100 per kg'},
    {'name': 'Kiwi', 'image': 'kiwi.png', 'price': '₹123 (3 pieces)'},
    {'name': 'DragonFruit', 'image': 'dragonfruit.png', 'price': '₹63 each'},
    {'name': 'Pineapple', 'image': 'pineapple.png', 'price': '₹93 each'},
    {'name': 'Strawberry', 'image': 'strawberry.png', 'price': '₹96 (1 pack)'},
    {'name': 'Grapes', 'image': 'grapes.png', 'price': '₹70 (500g)'},
    {'name': 'Carrot', 'image': 'carrot.png', 'price': '₹20 per kg'},
    {'name': 'Pomegranate', 'image': 'pomegranet.png', 'price': '₹115 (500g)'},
    {'name': 'Watermelon', 'image': 'watermelon.png', 'price': '₹35 each'},
    {'name': 'Muskmelon', 'image': 'muskmelon.png', 'price': '₹67 each'},
    {'name': 'Papaya', 'image': 'papaya.png', 'price': '₹111 per kg'},
     {'name': 'Maggi','image': 'maggi.png','price': '₹10 per each'},
        {'name': 'Tedhe Medhe','image': 'TedheMedhe.png','price': '₹10 per each'},
        {'name': "Lay's India's Magic Masala ",'image': 'BlueLays.png','price': '₹10 per each'},
        {'name': "Lay's Classic Salted ",'image': 'YellowLays.png','price': '₹10 per each'},
        {'name': "Lay's American Style Cream & Onion  ",'image': 'greenLays.png','price': '₹10 per each'},
        {'name': "Maggi Cheese Macroni Instant Pasta",'image': 'cheese.png','price': '₹35 per each'},
        {'name': "Maggi Masala Penne Instant Pasta",'image': 'masala.png','price': '₹35 per each'},
        {'name': "Oreo",'image': 'oreo.png','price': '₹10 per each'},
        {'name': "Dark Fantasy ",'image': 'DarkFantasy.png','price': '₹30 '},
        {'name': "Hide & Seek ",   'image': 'Hide.png','price': '₹30 per each' },
        {'name': "Jim Jam",'image': 'JimJam.png','price': '₹10 per each'},
        {'name': "Good Day",'image': 'Gooday.png','price': '₹10 per each'},
        { 'name': "Little Hearts",'image': 'Hearts.png','price': '₹10 per each'},
        {'name': "Ferrero Rocher",'image': 'Ferrero.png','price': '₹763 (24 pieces)'},
        {'name': "Dairy Milk Silk Fruit & Nut",'image': 'FruitNut.png','price': '₹186'},
        {'name': "Kit Kat",'image': 'Kitkat.png','price': '₹110'},
        {'name': "Crispello",'image': 'crispello.png','price': '₹40'},
        {'name': "Munch",'image': 'Munch.png','price': '₹57'},
        {'name': "ThumsUp",'image': 'ThumsUp.png','price': '₹40 (750ml)'},
        {'name': "Choco Latte",'image': 'ChocoLatte.png','price': '₹120'},
        {'name': "Cold Coffee",'image': 'ColdCoffee.png','price': '₹120'},
        {'name': "Diet Coke",'image': 'diet.png','price': '₹40 (300ml)'},
        {'name': "Fanta",'image': 'fanta.png','price': '₹40 (750ml)'},
        {'name': "Sprite",'image': 'sprite.png','price': '₹40 (750ml)'},
        {'name': "Limca",'image': 'limca.png','price': '₹40 (750ml)'},
        {'name': "Maza",'image': 'maza.png','price': '₹40 (600ml)'},
         {'name': "Mountain Dew",'image': 'dew.png','price': '₹86 (2 X 750ml)'},
        {'name': "Aloo Bhujia",'image': 'bhujia.png','price': '₹221 per kg'},
        {'name': "Kinder Joy",'image': 'joy.png','price': '₹48'},
        {'name': "Makhana",'image': 'makhana.png', 'price': '₹160 (100g)'},
        {'name': "Amul Moti Milk",'image': 'milk.png','price': '₹33 (450ml)'},
        {'name': "Whole Wheat Bread",'image': 'wheatBread.png','price': '₹60 (400g)'},
        {'name': "Brown Bread",'image': 'Brown.png','price': '₹55 (400g)'},
        {'name': "Bonn Pav Bread",'image': 'pav.png','price': '₹45 (250g)'},
        {'name': "Eggs",'image': 'eggs.png','price': '₹72 (6 pieces)'},
        {'name': "Kellogg's Corn Flakes",'image': 'flakes.png','price': '₹120 (250g)'},
        {'name': "Kellogg's Muesli Nuts Delight",'image': 'muesli.png','price': '₹544 (1 kg)'},
        {'name': "Saffola Masala Veggie Twist Oats",'image': 'oats.png','price': '₹68 (pack of 4)'},
        {'name': "Mother Dairy Classic Curd",'image': 'curd.png','price': '₹25 (200g)'},
        {'name': "Amul Salted Butter",'image': 'butter.png','price': '₹60 (100)'},
        {'name': "Amul Cheese Slices",'image': 'cheeseSlices.png','price': '₹85 (100g)'},
        {'name': "Amul Fresh Cream",'image': 'cream.png','price': '₹68 (250ml)'},
        {'name': "Nestle Milkmaid Sweetened Condensed Milk",'image': 'condensedMilk.png','price': '₹140 (380g)'},
        {'name': "MyFitness Chocolate Crunchy Peanut Butter (227 g)",'image': 'peanutButter.png','price': '₹146 (227g)'},
        {'name': "Dabur Honey",'image': 'honey.png','price': '₹115 (250g)'},
        {'name': "Kissan Fresh Tomato Ketchup",'image': 'ketchup.png','price': '₹100 (850g)'},
        {'name': "Veg Mayonnaise",'image': 'mayo.png','price': '₹49 (100g)'},
        {'name': "Ching's Secret Schezwan Chutney",'image': 'chutney.png','price': '₹84 (250g)'},
        {'name': "Hershey's Chocolate Syrup",'image': 'chocoSyrup.png','price': '₹105 (200g)'},
        {'name': "Smith & Jones Ginger Garlic Paste",'image': 'garlicpaste.png','price': '₹46 (200g)'},
        {'name': "Vinegar",'image': 'vinegar.png','price': '₹67 (610ml)'},
        {'name': "Tata Tea Premium Tea",'image': 'tata.png','price': '₹140 (250g)'},
        {'name': "Brooke Bond Taj Mahal Tea",'image': 'taj.png','price': '₹65 (100g)'},
        {'name': "Nescafe Classic - Instant Coffee Powder",'image': 'coffee.png','price': '₹230 (45g)'},
        {'name': "Aashirvaad Shudh Chakki Atta ",'image': 'ashirvad.png','price': '₹238 (5kg)'},
        {'name': "Fortune Chakki Fresh ",'image': 'fortune.png','price': '₹227 (5kg)'},
        {'name': "Daawat Rozana Gold Basmati Rice ",'image': 'rice.png','price': '₹415 (5kg)'},
        {'name': "Whole Farm Grocery Kabuli Chana ",'image': 'chana.png','price': '₹156 (1kg)'}, 
        {'name': "Whole Farm Premium Kashmiri Red Rajma ",'image': 'rajma.png','price': '₹120 (500g)'},  
        {'name': "Toor Dal ",'image': 'toor.png','price': '₹198 (1kg)'}, 
        {'name': "Urad Dal (Chilka)",'image': 'urad.png','price': '₹77 (500g)'}, 
        {'name': "Brown Chana ",'image': 'brownchana.png','price': '₹66 (500g)'}, 
        {'name': "Happydent White Spearmint Sugar Free Chewing Gum ",'image': 'happydent.png','price': '₹49'}, 
        {'name': "Parle Melody Chocolaty Candy",'image': 'melody.png','price': '₹100'}, 
        {'name': "Lotte Choco Pie",'image': 'pie.png','price': '₹80'}]
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
@app.route('/privacy_policy')
def policy():
    return render_template('privacy.html')
@app.route('/faq')
def faq():
    return render_template('faq.html')
@app.route('/terms')
def terms():
    return render_template('terms.html')
# Custom error handler for 500 Internal Server Error
@app.errorhandler(500)
def internal_error(error):
    return "An internal error occurred", 500
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower()  
    if query:
       results = [product for product in fruits_vegetables_dict if query in product['name'].lower()]
    else:
        results = fruits_vegetables_dict
    
    return render_template('search_results.html', query=query, results=results)




if __name__ == "__main__":
    app.run(debug=True, port=8080)