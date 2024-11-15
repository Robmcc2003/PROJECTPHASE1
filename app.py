from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from models import FencingEquipment, Cart, User

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# In-memory database for demonstration purposes
users = {
    'admin': User('admin', 'adminpass', 'admin'),
    'user': User('user', 'userpass', 'user')
}

# Products list
products = [
    # Blades
    FencingEquipment("Foil Blade", "A lightweight foil blade.", "Blade", 50.0, 10, blade_length=90, material="Steel",
                     weight=500, brand="BrandA", image_url="/static/uploads/FoilBlade.jpg"),
    FencingEquipment("Épée Blade", "A medium-weight épée blade.", "Blade", 60.0, 8, blade_length=110, material="Alloy",
                     weight=600, brand="BrandB", image_url="/static/uploads/EpeeBlade.jpg"),
    FencingEquipment("Sabre Blade", "A sabre blade for advanced fencers.", "Blade", 70.0, 5, blade_length=105,
                     material="Carbon Fiber", weight=550, brand="BrandC", image_url="/static/uploads/SabreBlade.jpg"),
    FencingEquipment("Practice Foil", "Perfect for beginners and training sessions.", "Blade", 45.0, 20,
                     blade_length=85, material="Aluminum", weight=450, brand="BrandD",
                     image_url="/static/uploads/PracticeFoil.jpg"),
    FencingEquipment("Competition Épée", "Ideal for professional épée competitions.", "Blade", 80.0, 7,
                     blade_length=115, material="Titanium Alloy", weight=620, brand="BrandE",
                     image_url="/static/uploads/CompetitionEpee.jpg"),
    FencingEquipment("Premium Sabre", "A high-quality sabre for expert fencers.", "Blade", 95.0, 4, blade_length=100,
                     material="High-Carbon Steel", weight=560, brand="BrandF",
                     image_url="/static/uploads/PremiumSabre.jpg"),

    # Jackets
    FencingEquipment("Lightweight Jacket", "Breathable and flexible jacket.", "Jacket", 55.0, 20, size="Small",
                     material="Polyester", brand="BrandZ", image_url="/static/uploads/LightweightJacket.jpg"),
    FencingEquipment("Padded Jacket", "Extra padding for added protection.", "Jacket", 80.0, 12, size="Large",
                     material="Kevlar", brand="BrandW", image_url="/static/uploads/PaddedJacket.jpg"),
]

cart = Cart()

# Helper functions
def is_logged_in():
    return 'username' in session

def is_logged_in_as(role):
    return session.get('role') == role

# Home route
@app.route('/')
def home():
    return render_template('index.html', products=enumerate(products))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user.password == password:
            session['username'] = username
            session['role'] = user.role
            log_user_activity("Logged in", username)  # Log user login
            flash(f"Logged in as {user.role}", "success")
            return redirect(url_for('home'))
        else:
            flash("Incorrect username or password.", "danger")
    return render_template('login.html')


@app.route('/update_delivery_fee/<int:product_id>', methods=['POST'])
def update_delivery_fee(product_id):
    if session.get('role') != 'admin':
        flash("Access denied. Admins only.")
        return redirect(url_for('admin_dashboard'))

    new_delivery_fee = float(request.form['delivery_fee'])
    if 0 <= product_id < len(products):
        products[product_id].delivery_fee = new_delivery_fee
        flash(f"Delivery fee updated for {products[product_id].name}.")

    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    username = session.get('username')
    if username:
        log_user_activity("Logged out", username)  # Log user logout
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
    return render_template('register.html')

# Product detail route
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    if 0 <= product_id < len(products):
        product = products[product_id]
        return render_template('product.html', product=product, product_id=product_id)
    return redirect(url_for('home'))

@app.route('/cart')
def view_cart():
    if not is_logged_in():
        flash("Please log in to view your cart.", "warning")
        return redirect(url_for('login'))

    # Initialize totals
    product_total = 0
    total_delivery_fee = 0

    # Calculate totals based on cart items
    for item, quantity in cart.items:
        product_total += item.price * quantity
        total_delivery_fee += item.delivery_fee * quantity

    # Grand total includes both product total and delivery fees
    grand_total = product_total + total_delivery_fee

    return render_template(
        'cart.html',
        cart=cart.items,
        product_total=product_total,
        total_delivery_fee=total_delivery_fee,
        grand_total=grand_total
    )


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    username = session.get('username')
    if not is_logged_in() or session.get('role') not in ['admin', 'user']:
        flash("Please log in as an admin or user to add items to the cart.", "warning")
        return redirect(url_for('login'))

    if 0 <= product_id < len(products):
        product = products[product_id]
        quantity = int(request.form['quantity'])
        cart.add_item(product, quantity)
        log_user_activity(f"Added {quantity} of {product.name} to cart", username)  # Log item addition
        flash(f"Added {quantity} of {product.name} to your cart.", "success")
    return redirect(url_for('view_cart'))


# List to store sales records and user activities (if not using a database)
sales = []
user_activities = []

def log_sale(cart):
    """Logs completed sales with details of each product and quantity."""
    items_list = [dict(name=item.name, quantity=quantity, price=item.price) for item, quantity in cart.items]
    total = calculate_total(cart)
    sale_record = {
        "date": datetime.now(),
        "sale_items": items_list,  # Renamed from `items` to `items_list` to avoid conflicts
        "total": total
    }
    sales.append(sale_record)

def log_user_activity(action, username):
    """Logs user actions with a timestamp."""
    activity_record = {
        "date": datetime.now(),
        "username": username,
        "action": action
    }
    user_activities.append(activity_record)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    username = session.get('username')
    if not is_logged_in() or session.get('role') not in ['admin', 'user']:
        flash("Please log in to proceed with checkout.", "warning")
        return redirect(url_for('login'))

    # Check stock and complete checkout
    for item, quantity in cart.items:
        if item.stock < quantity:
            flash(f"Not enough stock for {item.name}. Only {item.stock} left in stock.", "danger")
            return redirect(url_for('view_cart'))

    for item, quantity in cart.items:
        item.stock -= quantity

    # Log the sale
    log_sale(cart)
    log_user_activity("Completed checkout", username)  # Log checkout

    # Clear the cart
    cart.items.clear()

    flash("Checkout complete! Thank you for your purchase.", "success")
    return redirect(url_for('home'))


def calculate_total(cart):
    """
    Calculate the total cost of items in the cart, including delivery fees.
    """
    return sum((item.price + item.delivery_fee) * quantity for item, quantity in cart.items)


@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Admin access required.", "danger")
        return redirect(url_for('home'))

    return render_template('admin_dashboard.html', products=products, users=users, sales=sales,
                           user_activities=user_activities)

@app.route('/admin/edit_user/<username>', methods=['GET', 'POST'])
def edit_user(username):
    if not is_logged_in_as('admin'):
        flash("Admin access required.", "danger")
        return redirect(url_for('home'))

    user = users.get(username)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        user.role = request.form['role']
        flash("User updated successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_user.html', username=username, user=user)

@app.route('/admin/delete_user/<username>', methods=['POST'])
def delete_user(username):
    if not is_logged_in_as('admin'):
        flash("Admin access required.", "danger")
        return redirect(url_for('home'))

    if username in users:
        del users[username]
        log_user_activity(f"Deleted user {username}", session.get('username'))  # Log user deletion
        flash(f"User '{username}' has been deleted.", "success")
    else:
        flash("User not found.", "danger")
    return redirect(url_for('admin_dashboard'))

# Route for editing a product
@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'username' not in session or session.get('role') != 'admin':
        flash("Admin access required.", "danger")
        return redirect(url_for('home'))

    # Check if product exists
    if 0 <= product_id < len(products):
        product = products[product_id]

        if request.method == 'POST':
            # Update product fields (excluding image)
            product.name = request.form['name']
            product.description = request.form['description']
            product.price = float(request.form['price'])
            product.stock = int(request.form['stock'])
            product.blade_length = float(request.form['blade_length'])
            product.material = request.form['material']
            product.weight = float(request.form['weight'])

            flash("Product updated successfully.", "success")
            return redirect(url_for('admin_dashboard'))

        return render_template('edit_product.html', product=product)

    flash("Product not found.", "warning")
    return redirect(url_for('admin_dashboard'))

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

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not is_logged_in_as('admin'):
        flash("Admin access required to delete products.", "danger")
        return redirect(url_for('home'))

    if 0 <= product_id < len(products):
        deleted_product = products.pop(product_id)
        log_user_activity(f"Deleted product {deleted_product.name}", session.get('username'))  # Log product deletion
        flash(f"Product '{deleted_product.name}' has been deleted.", "success")
    else:
        flash("Invalid product ID.", "danger")

    return redirect(url_for('admin_dashboard'))


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=5001)
