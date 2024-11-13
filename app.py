# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import FencingEquipment, Cart, User

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# In-memory database for demonstration purposes
users = {
    'admin': User('admin', 'adminpass', 'admin'),
    'user': User('user', 'userpass', 'user')
}
# Assuming 'products' is a list of FencingEquipment instances
products = [
    FencingEquipment("Foil Blade", "A lightweight foil blade.", 50.0, 10, 90, "Steel", 500, "BrandA", image_url="/static/uploads/FoilBlade.jpg"),
    FencingEquipment("Épée Blade", "A medium-weight épée blade.", 60.0, 8, 110, "Alloy", 600, "BrandB", image_url="/static/uploads/EpeeBlade.jpg"),
    FencingEquipment("Sabre Blade", "A sabre blade for advanced fencers.", 70.0, 5, 105, "Carbon Fiber", 550, "BrandC", image_url="/static/uploads/SabreBlade.jpg"),
FencingEquipment("Practice Foil", "Perfect for beginners and training sessions.", 45.0, 20, 85, "Aluminum", 450, "BrandD", image_url="/static/uploads/PracticeFoil.jpg"),
    FencingEquipment("Competition Épée", "Ideal for professional épée competitions.", 80.0, 7, 115, "Titanium Alloy", 620, "BrandE", image_url="/static/uploads/CompetitionEpee.jpg"),
    FencingEquipment("Premium Sabre", "A high-quality sabre for expert fencers.", 95.0, 4, 100, "High-Carbon Steel", 560, "BrandF", image_url="/static/uploads/PremiumSabre.jpg")
]

cart = Cart()


# Helper functions to check login status and role
def is_logged_in():
    return 'username' in session


def is_logged_in_as(role):
    return session.get('role') == role


# Home route
@app.route('/')
def home():
    return render_template('index.html', products=enumerate(products))


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)

        if user and user.password == password:
            session['username'] = username
            session['role'] = user.role
            flash(f"Logged in as {user.role}", "success")
            return redirect(url_for('home'))
        else:
            flash("Incorrect username or password.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('home'))


# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = User(username, password, 'user')
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Username already exists.", "warning")
            return redirect(url_for('register'))
    return render_template('register.html')


# Product detail route
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    if 0 <= product_id < len(products):
        product = products[product_id]
        return render_template('product.html', product=product, product_id=product_id)
    return redirect(url_for('home'))


# Cart view route
@app.route('/cart')
def view_cart():
    if not is_logged_in():
        flash("Please log in to view your cart.", "warning")
        return redirect(url_for('login'))
    return render_template('cart.html', cart=cart.items, total=cart.total_price())


# Add to cart route
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not is_logged_in() or session.get('role') not in ['admin', 'user']:
        flash("Please log in as an admin or user to add items to the cart.", "warning")
        return redirect(url_for('login'))

    if 0 <= product_id < len(products):
        product = products[product_id]
        quantity = int(request.form['quantity'])
        cart.add_item(product, quantity)
        flash(f"Added {quantity} of {product.name} to your cart.", "success")
    return redirect(url_for('view_cart'))


# Checkout route
@app.route('/checkout')
def checkout():
    if not is_logged_in() or session.get('role') not in ['admin', 'user']:
        flash("Please log in to proceed with checkout.", "warning")
        return redirect(url_for('login'))
    flash("Checkout complete! Thank you for your purchase.", "success")
    cart.items.clear()  # Empty the cart after checkout
    return redirect(url_for('home'))


# Admin dashboard route
@app.route('/admin')
def admin_dashboard():
    if not is_logged_in_as('admin'):
        flash("Admin access required.", "danger")
        return redirect(url_for('home'))
    return render_template('admin_dashboard.html', products=products, users=users)


# Create product route (admin only)
@app.route('/admin/create_product', methods=['GET', 'POST'])
def create_product():
    if not is_logged_in_as('admin'):
        flash("Admin access required to create products.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        blade_length = float(request.form['blade_length'])
        material = request.form['material']
        weight = float(request.form['weight'])
        brand = request.form['brand']

        new_product = FencingEquipment(name, description, price, stock, blade_length, material, weight, brand)
        products.append(new_product)
        flash("Product created successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('create_product.html')


# Edit product route (admin only)
@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not is_logged_in_as('admin'):
        flash("Admin access required to edit products.", "danger")
        return redirect(url_for('home'))

    if 0 <= product_id < len(products):
        product = products[product_id]

        if request.method == 'POST':
            product.name = request.form['name']
            product.description = request.form['description']
            product.price = float(request.form['price'])
            product.stock = int(request.form['stock'])
            product.blade_length = float(request.form['blade_length'])
            product.material = request.form['material']
            product.weight = float(request.form['weight'])
            product.brand = request.form['brand']

            flash("Product updated successfully.", "success")
            return redirect(url_for('admin_dashboard'))

        return render_template('edit_product.html', product=product)
    return redirect(url_for('admin_dashboard'))


# Delete product route (admin only)
@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not is_logged_in_as('admin'):
        flash("Admin access required to delete products.", "danger")
        return redirect(url_for('home'))

    if 0 <= product_id < len(products):
        deleted_product = products.pop(product_id)
        flash(f"Product '{deleted_product.name}' has been deleted.", "success")
    else:
        flash("Invalid product ID.", "danger")

    return redirect(url_for('admin_dashboard'))


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=5001)
