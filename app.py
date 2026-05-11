from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import inspect, text
import os
from datetime import datetime, timedelta
<<<<<<< HEAD
from models import db, Vegetable, Order, OrderItem, Feedback, Admin, Notification
=======
from models import db, Vegetable, Order, OrderItem, Feedback, Admin
>>>>>>> f0cf3aaebcdfadd57343fa47bc5a5c138a69e28b
from config import config
from utils import generate_payment_qr_code
import logging

def ensure_feedback_rating_column():
    inspector = inspect(db.engine)
    if 'feedback' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('feedback')]
        if 'rating' not in columns:
            if db.engine.dialect.name == 'sqlite':
                db.session.execute(text('ALTER TABLE feedback ADD COLUMN rating INTEGER DEFAULT 5'))
            else:
                db.session.execute(text('ALTER TABLE feedback ADD COLUMN rating INTEGER DEFAULT 5'))
            db.session.commit()




from flask import Flask

app = Flask(__name__)

def create_app(config_name=None):
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
<<<<<<< HEAD
    # Add secret key for CSRF protection (use from config or generate)
    if 'SECRET_KEY' not in app.config:
        app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
=======
    # Configure logging
    if not app.debug:
        logging.basicConfig(filename='app.log', level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO)
    
    app.logger = logging.getLogger(__name__)
    
    db.init_app(app)
    app.jinja_env.globals['timedelta'] = timedelta

    with app.app_context():
        db.create_all()
        ensure_feedback_rating_column()
>>>>>>> f0cf3aaebcdfadd57343fa47bc5a5c138a69e28b
    
    # Initialize extensions
    db.init_app(app)
    csrf = CSRFProtect(app)
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    # Ensure upload folder exists
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except Exception as e:
        print(f"Could not create upload folder: {e}")
    
    return app, csrf, limiter

# Create app instance first
app, csrf, limiter = create_app()

# Initialize database and seed data on startup
def _initialize_db_on_import():
    """Initialize database when app is imported (for Render/Gunicorn)"""
    with app.app_context():
        try:
            db.create_all()
            
            # Create default admin if not exists
            if Admin.query.count() == 0:
                default_admin = Admin(username='admin')
                default_admin.set_password('admin123')
                db.session.add(default_admin)
                db.session.commit()
                print("✅ Default admin account created: username='admin', password='admin123'")
            
            # Seed vegetables if empty
            if Vegetable.query.count() == 0:
                seed_data = [
                    {'name': 'Tomatoes', 'price': 40.0, 'stock': 50, 'description': 'Fresh red tomatoes from our farm'},
                    {'name': 'Potatoes', 'price': 30.0, 'stock': 100, 'description': 'High quality potatoes'},
                    {'name': 'Onions', 'price': 35.0, 'stock': 75, 'description': 'Fresh onions'},
                    {'name': 'Carrots', 'price': 45.0, 'stock': 60, 'description': 'Sweet and crunchy carrots'},
                    {'name': 'Spinach', 'price': 25.0, 'stock': 40, 'description': 'Fresh green spinach'},
                    {'name': 'Broccoli', 'price': 60.0, 'stock': 30, 'description': 'Organic broccoli'},
                    {'name': 'Bell Peppers', 'price': 55.0, 'stock': 45, 'description': 'Colorful bell peppers'},
                    {'name': 'Cucumbers', 'price': 35.0, 'stock': 55, 'description': 'Fresh cucumbers'},
                    {'name': 'Cabbage', 'price': 28.0, 'stock': 35, 'description': 'Green cabbage'},
                    {'name': 'Cauliflower', 'price': 50.0, 'stock': 25, 'description': 'Fresh cauliflower'}
                ]
                
                for data in seed_data:
                    vegetable = Vegetable(**data)
                    db.session.add(vegetable)
                
                db.session.commit()
                print("✅ Database seeded with 10 sample vegetables")
            
            print("✅ Database initialization complete")
        except Exception as e:
            print(f"⚠️ Database initialization error: {e}")

# Call initialization immediately on import
_initialize_db_on_import()

# Now define all routes using the created app
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Database initialization flag
_db_initialized = False

def ensure_db_initialized():
    """Initialize database tables if not already done"""
    global _db_initialized
    if _db_initialized:
        return
    
    try:
        with app.app_context():
            db.create_all()
            _db_initialized = True
    except Exception as e:
        print(f"Database initialization error: {e}")

@app.route('/')
def home():
    ensure_db_initialized()
    vegetables = Vegetable.query.filter(Vegetable.stock > 0).all()
    return render_template('home.html', vegetables=vegetables)

@app.route('/vegetables')
def vegetables():
    vegetables = Vegetable.query.filter(Vegetable.stock > 0).all()
    return render_template('home.html', vegetables=vegetables)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/vision')
def vision():
    return render_template('vision.html')

@app.route('/process')
def process():
    return render_template('process.html')

@app.route('/api/vegetables')
def api_vegetables():
    vegetables = Vegetable.query.all()
    return jsonify([veg.to_dict() for veg in vegetables])

@app.route('/api/cart-count')
def api_cart_count():
    cart = session.get('cart', {})
    return jsonify({'count': len(cart)})

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    cart_total = 0
    cart_details = []
    
    for veg_id, item in cart_items.items():
        vegetable = Vegetable.query.get(int(veg_id))
        if vegetable:
            subtotal = vegetable.price * item['quantity']
            cart_total += subtotal
            cart_details.append({
                'vegetable': vegetable,
                'quantity': item['quantity'],
                'subtotal': subtotal
            })
    
    return render_template('cart.html', cart_items=cart_details, cart_total=cart_total)

@app.route('/add_to_cart/<int:veg_id>')
def add_to_cart(veg_id):
    vegetable = Vegetable.query.get_or_404(veg_id)
    
    if vegetable.stock <= 0:
        flash('This vegetable is out of stock!', 'error')
        return redirect(url_for('home'))
    
    cart = session.get('cart', {})
    
    if str(veg_id) in cart:
        if cart[str(veg_id)]['quantity'] < vegetable.stock:
            cart[str(veg_id)]['quantity'] += 1
            flash(f'{vegetable.name} added to cart!', 'success')
        else:
            flash(f'Only {vegetable.stock} {vegetable.name}(s) available in stock!', 'error')
    else:
        cart[str(veg_id)] = {'quantity': 1}
        flash(f'{vegetable.name} added to cart!', 'success')
    
    session['cart'] = cart
    return redirect(url_for('home'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    veg_id = request.form.get('veg_id')
    quantity = request.form.get('quantity', type=int)
    
    if quantity <= 0:
        cart = session.get('cart', {})
        if str(veg_id) in cart:
            del cart[str(veg_id)]
        session['cart'] = cart
        return jsonify({'success': True, 'message': 'Item removed from cart'})
    
    vegetable = Vegetable.query.get(veg_id)
    if not vegetable or quantity > vegetable.stock:
        return jsonify({'success': False, 'message': 'Invalid quantity or insufficient stock'})
    
    cart = session.get('cart', {})
    cart[str(veg_id)] = {'quantity': quantity}
    session['cart'] = cart
    
    # Calculate new totals
    cart_total = 0
    for item_veg_id, item in cart.items():
        veg = Vegetable.query.get(int(item_veg_id))
        if veg:
            cart_total += veg.price * item['quantity']
    
    return jsonify({
        'success': True, 
        'message': 'Cart updated',
        'subtotal': vegetable.price * quantity,
        'cart_total': cart_total
    })

@app.route('/remove_from_cart/<int:veg_id>')
def remove_from_cart(veg_id):
    cart = session.get('cart', {})
    if str(veg_id) in cart:
        del cart[str(veg_id)]
        session['cart'] = cart
        flash('Item removed from cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
<<<<<<< HEAD
        rating = request.form.get('rating', type=int, default=5)
=======
        rating = request.form.get('rating', type=int)
>>>>>>> f0cf3aaebcdfadd57343fa47bc5a5c138a69e28b
        
        if not name or not message:
            flash('Please fill in all required fields!', 'error')
            return redirect(url_for('contact'))
        
<<<<<<< HEAD
        # Save feedback to database including rating
        feedback = Feedback(name=name, email=email, message=message, rating=rating)
=======
        if rating is None or rating < 1 or rating > 5:
            rating = 5
        
        # Save feedback to database
        feedback = Feedback(name=name, email=email, rating=rating, message=message)
>>>>>>> f0cf3aaebcdfadd57343fa47bc5a5c138a69e28b
        db.session.add(feedback)
        db.session.commit()
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_items = session.get('cart', {})
    
    if not cart_items:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('cart'))
    
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        email = request.form.get('email')
        delivery_time = request.form.get('delivery_time')
        order_notes = request.form.get('notes')
        payment_method = request.form.get('payment_method', 'cod')
        
        # Basic validation
        import re
        if not customer_name or len(customer_name.strip()) < 2:
            flash('Please enter a valid name (at least 2 characters)', 'error')
            return redirect(url_for('checkout'))
        
        if not phone or not re.match(r'^\d{10}$', phone):
            flash('Please enter a valid 10-digit phone number', 'error')
            return redirect(url_for('checkout'))
        
        if not address or len(address.strip()) < 5:
            flash('Please enter a complete delivery address', 'error')
            return redirect(url_for('checkout'))
        
        if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash('Please enter a valid email address', 'error')
            return redirect(url_for('checkout'))
        
        if payment_method not in ['cod', 'upi', 'qr']:
            flash('Please select a valid payment method', 'error')
            return redirect(url_for('checkout'))
        
        # Calculate total and create order
        total = 0
        order_items_data = []
        
        # Check stock availability FIRST
        for veg_id, item in cart_items.items():
            vegetable = Vegetable.query.get(int(veg_id))
            if not vegetable:
                flash(f'Product not found!', 'error')
                return redirect(url_for('checkout'))
            
            if vegetable.stock < item['quantity']:
                flash(f'Sorry, {vegetable.name} only has {vegetable.stock}kg in stock, but you ordered {item["quantity"]}kg!', 'error')
                return redirect(url_for('cart'))
            
            subtotal = vegetable.price * item['quantity']
            total += subtotal
            order_items_data.append({
                'vegetable': vegetable,
                'quantity': item['quantity'],
                'price': vegetable.price
            })
        
<<<<<<< HEAD
        # Create order with pending status by default
        order = Order(
            customer_name=customer_name,
            phone=phone,
            address=address,
            email=email,
            total=total,
            payment_method=payment_method,
            delivery_time=delivery_time,
            order_notes=order_notes,
            status='pending'  # Set status explicitly
        )
        db.session.add(order)
        db.session.commit()
        
        # Create order items (but don't commit yet for QR payment)
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                vegetable_id=item_data['vegetable'].id,
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Create notification for admin
        notification = Notification(
            title=f'New Order #{order.id}',
            message=f'New order from {customer_name}: ₹{total} - {len(order_items_data)} items',
            type='order',
            order_id=order.id
        )
        db.session.add(notification)
        db.session.commit()
        
        # Handle different payment methods
        if payment_method == 'upi':
            session['temp_cart'] = cart_items  # Store for recovery if needed
            return redirect(url_for('payment', order_id=order.id))
        elif payment_method == 'qr':
            session['temp_cart'] = cart_items  # Store for recovery if needed
            return redirect(url_for('qr_payment', order_id=order.id))
        elif payment_method == 'cod':
            # For COD, update stock immediately and mark order as confirmed
            for veg_id, item in cart_items.items():
                vegetable = Vegetable.query.get(int(veg_id))
                if vegetable:
                    vegetable.stock -= item['quantity']
            
            # Mark order as confirmed for COD
            order.status = 'confirmed'
            db.session.commit()
            
            # Clear cart BEFORE redirect to ensure it's cleared
            session.pop('cart', None)
            session.pop('temp_cart', None)
            session.modified = True
            
            flash(f'Order placed successfully! Order ID: {order.id}', 'success')
            return redirect(url_for('order_confirmation', order_id=order.id))
        
        return redirect(url_for('payment', order_id=order.id))
=======
        # Use transaction for atomic operation
        try:
            with db.session.begin_nested():
                # Check stock availability again and update atomically
                for item_data in order_items_data:
                    veg = item_data['vegetable']
                    if veg.stock < item_data['quantity']:
                        raise ValueError(f'Insufficient stock for {veg.name}')
                    veg.stock -= item_data['quantity']
                
                # Create order
                order = Order(
                    customer_name=customer_name,
                    phone=phone,
                    address=address,
                    email=email,
                    total=total,
                    payment_method=payment_method,
                    delivery_time=delivery_time,
                    order_notes=order_notes
                )
                db.session.add(order)
                db.session.flush()  # Get order.id
                
                # Create order items
                for item_data in order_items_data:
                    order_item = OrderItem(
                        order_id=order.id,
                        vegetable_id=item_data['vegetable'].id,
                        quantity=item_data['quantity'],
                        price=item_data['price']
                    )
                    db.session.add(order_item)
                
                db.session.commit()
                session['cart'] = {}
                if payment_method == 'cod':
                    flash('Your order has been placed successfully. Please keep the amount ready for delivery.', 'success')
                    return redirect(url_for('order_confirmation', order_id=order.id))
                else:
                    flash('Your order has been created. Please complete payment to confirm your order.', 'success')
                    return redirect(url_for('payment', order_id=order.id))
        except ValueError as e:
            db.session.rollback()
            app.logger.warning(f"Checkout failed for {customer_name}: {str(e)}")
            flash(str(e), 'error')
            return redirect(url_for('checkout'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Checkout error for {customer_name}: {str(e)}")
            flash('An error occurred while processing your order. Please try again.', 'error')
            return redirect(url_for('checkout'))
>>>>>>> f0cf3aaebcdfadd57343fa47bc5a5c138a69e28b
    
    # Calculate total for display
    cart_total = 0
    cart_details = []
    
    for veg_id, item in cart_items.items():
        vegetable = Vegetable.query.get(int(veg_id))
        if vegetable:
            subtotal = vegetable.price * item['quantity']
            cart_total += subtotal
            cart_details.append({
                'vegetable': vegetable,
                'quantity': item['quantity'],
                'subtotal': subtotal
            })
    
    return render_template('checkout.html', cart_items=cart_details, cart_total=cart_total)

@app.route('/payment/<int:order_id>')
def payment(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Get cart items for display
    cart_items = []
    cart_total = 0
    
    # Reconstruct cart from order items
    for item in order.order_items:
        cart_total += item.price * item.quantity
        cart_items.append({
            'vegetable': item.vegetable,
            'quantity': item.quantity,
            'subtotal': item.price * item.quantity
        })
    
    return render_template('payment.html', order=order, cart_items=cart_items, cart_total=cart_total)

@app.route('/process_payment/<int:order_id>', methods=['POST'])
def process_payment(order_id):
    order = Order.query.get_or_404(order_id)
    payment_method = request.form.get('payment_method')
    
    if payment_method == 'cod':
        # COD is already handled in checkout
        return redirect(url_for('order_confirmation', order_id=order.id))
    elif payment_method == 'qr':
        return redirect(url_for('qr_payment', order_id=order.id))
    else:
        flash('Invalid payment method selected!', 'error')
        return redirect(url_for('payment', order_id=order_id))

@app.route('/qr_payment/<int:order_id>')
def qr_payment(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Get cart items for display
    cart_items = []
    cart_total = 0
    
    # Reconstruct cart from order items
    for item in order.order_items:
        cart_total += item.price * item.quantity
        cart_items.append({
            'vegetable': item.vegetable,
            'quantity': item.quantity,
            'subtotal': item.price * item.quantity
        })
    
    # Generate QR code
    qr_data = generate_payment_qr_code(order_id, cart_total)
    
    return render_template('qr_payment.html', order=order, cart_items=cart_items, cart_total=cart_total, qr_data=qr_data)

@app.route('/verify_qr_payment/<int:order_id>', methods=['POST'])
def verify_qr_payment(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Complete the order after the customer confirms payment
    order.payment_method = 'upi'
    order.payment_status = 'completed'
    order.status = 'confirmed'
    
    # Stock is already updated during checkout
    db.session.commit()
    
<<<<<<< HEAD
    # Clear cart BEFORE redirect to ensure it's cleared
    session.pop('cart', None)
    session.pop('temp_cart', None)
    session.modified = True
=======
    # Clear cart for the session
    session['cart'] = {}
>>>>>>> f0cf3aaebcdfadd57343fa47bc5a5c138a69e28b
    
    app.logger.info(f"Order {order.id} payment confirmed for {order.customer_name}")
    flash('Payment confirmed! Your order is complete.', 'success')
    return redirect(url_for('order_confirmation', order_id=order.id))

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    order_items = []
    for item in order.order_items:
        order_items.append({
            'vegetable': item.vegetable,
            'quantity': item.quantity,
            'price': item.price,
            'subtotal': item.price * item.quantity
        })
    session['cart'] = {}
    return render_template('order_confirmation.html', order=order, order_items=order_items)

@app.route('/track_order')
def track_order():
    order_id = request.args.get('order_id', type=int)
    email = request.args.get('email')
    if order_id and email:
        order = Order.query.filter_by(id=order_id, email=email).first()
        if order:
            order_items = []
            for item in order.order_items:
                order_items.append({
                    'vegetable': item.vegetable,
                    'quantity': item.quantity,
                    'price': item.price,
                    'subtotal': item.price * item.quantity
                })
            return render_template('order_status.html', order=order, order_items=order_items)
        flash('Order not found. Please verify your Order ID and email.', 'error')
    return render_template('track_order.html')

@app.route('/razorpay_success/<int:order_id>', methods=['POST'])
def razorpay_success(order_id):
    order = Order.query.get_or_404(order_id)
    order.payment_method = 'razorpay'
    order.payment_status = 'completed'
    order.status = 'confirmed'
    db.session.commit()
    session['cart'] = {}
    flash('Payment successful! Your order is confirmed.', 'success')
    return redirect(url_for('order_confirmation', order_id=order.id))

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def admin_login():
    ensure_db_initialized()
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Track failed login attempts in session
        failed_attempts = session.get('failed_login_attempts', 0)
        
        # Lock account temporarily after 5 failed attempts
        if failed_attempts >= 5:
            flash('Too many login attempts. Please try again in 15 minutes.', 'error')
            return render_template('admin_login.html')
        
        # Validate inputs
        if not username or not password:
            flash('Please enter both username and password!', 'error')
            return render_template('admin_login.html')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            # Clear failed attempts on successful login
            session.pop('failed_login_attempts', None)
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=24)
            login_user(admin, remember=True)
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            # Increment failed attempts
            failed_attempts += 1
            session['failed_login_attempts'] = failed_attempts
            
            # Generic error message for security (don't reveal if username exists)
            if failed_attempts >= 5:
                flash('Too many failed attempts. Please try again later.', 'error')
            else:
                flash('Invalid username or password!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/change_password', methods=['GET', 'POST'])
@login_required
def admin_change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            flash('Please fill in all fields!', 'error')
            return redirect(url_for('admin_change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match!', 'error')
            return redirect(url_for('admin_change_password'))
        
        admin = Admin.query.get(current_user.id)
        if admin and admin.check_password(current_password):
            admin.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Current password is incorrect!', 'error')
    
    return render_template('admin_change_password.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    ensure_db_initialized()  # Make sure DB is ready
    
    try:
        # Force fresh data from database without caching
        db.session.expire_all()  # Clear session cache
        
        # Get all orders
        orders = Order.query.order_by(Order.date.desc()).all()
        
        # Count orders by status
        total_orders = len(orders)
        pending_orders = sum(1 for order in orders if order.status == 'pending')
        confirmed_orders = sum(1 for order in orders if order.status == 'confirmed')
        completed_orders = sum(1 for order in orders if order.status == 'completed')
        
        # Get vegetables and feedbacks
        feedbacks = Feedback.query.order_by(Feedback.date.desc()).limit(5).all()
<<<<<<< HEAD
        vegetables = Vegetable.query.all()
        total_vegetables = len(vegetables)
        total_feedback = Feedback.query.count()
        
        # Get all notifications (unread + recent read)
        all_notifications = Notification.query.order_by(Notification.created_at.desc()).limit(20).all()
        unread_count = Notification.query.filter_by(is_read=False).count()
        total_revenue = sum(order.total for order in orders)
        
        print(f"✅ Dashboard - Orders: {total_orders}, Pending: {pending_orders}, Confirmed: {confirmed_orders}, Vegetables: {total_vegetables}")
        
=======
        total_vegetables = Vegetable.query.count()
        total_feedbacks = Feedback.query.count()
>>>>>>> f0cf3aaebcdfadd57343fa47bc5a5c138a69e28b
    except Exception as e:
        print(f"⚠️ Database error in dashboard: {e}")
        import traceback
        traceback.print_exc()
        
        orders = []
        total_orders = 0
        pending_orders = 0
        confirmed_orders = 0
        completed_orders = 0
        feedbacks = []
        total_vegetables = 0
<<<<<<< HEAD
        total_feedback = 0
        all_notifications = []
        unread_count = 0
        total_revenue = 0
=======
        total_feedbacks = 0
>>>>>>> f0cf3aaebcdfadd57343fa47bc5a5c138a69e28b
    
    response = make_response(render_template('admin_dashboard.html', 
                         orders=orders, 
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         confirmed_orders=confirmed_orders,
                         completed_orders=completed_orders,
                         feedbacks=feedbacks,
                         total_vegetables=total_vegetables,
<<<<<<< HEAD
                         total_feedback=total_feedback,
                         notifications=all_notifications,
                         unread_count=unread_count,
                         total_revenue=total_revenue))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
=======
                         total_feedbacks=total_feedbacks)
>>>>>>> f0cf3aaebcdfadd57343fa47bc5a5c138a69e28b

@app.route('/admin/products')
@login_required
def admin_products():
    try:
        vegetables = Vegetable.query.all()
    except Exception as e:
        print(f"Database error: {e}")
        vegetables = []
    return render_template('admin_products.html', vegetables=vegetables)

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price', type=float)
        stock = request.form.get('stock', type=int)
        description = request.form.get('description')
        
        if not all([name, price, stock]):
            flash('Please fill in all required fields!', 'error')
            return redirect(url_for('add_product'))
        
        # Handle image upload
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        vegetable = Vegetable(
            name=name,
            price=price,
            stock=stock,
            image=image,
            description=description
        )
        db.session.add(vegetable)
        db.session.commit()
        
        flash(f'{name} added successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('add_product.html')

@app.route('/admin/edit_product/<int:veg_id>', methods=['GET', 'POST'])
@login_required
def edit_product(veg_id):
    vegetable = Vegetable.query.get_or_404(veg_id)
    
    if request.method == 'POST':
        vegetable.name = request.form.get('name')
        vegetable.price = request.form.get('price', type=float)
        vegetable.stock = request.form.get('stock', type=int)
        vegetable.description = request.form.get('description')
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                vegetable.image = filename
        
        db.session.commit()
        flash(f'{vegetable.name} updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('edit_product.html', vegetable=vegetable)

@app.route('/admin/delete_product/<int:veg_id>')
@login_required
def delete_product(veg_id):
    try:
        vegetable = Vegetable.query.get_or_404(veg_id)
        vegetable_name = vegetable.name
        
        # Delete all order items associated with this vegetable
        OrderItem.query.filter_by(vegetable_id=veg_id).delete()
        
        # Delete the vegetable
        db.session.delete(vegetable)
        db.session.commit()
        
        flash(f'{vegetable_name} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Delete error: {str(e)}")
        flash(f'Error deleting product: {str(e)}', 'danger')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/update_order_status/<int:order_id>')
@login_required
def update_order_status(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        
        # Only mark as completed if order is confirmed (stock already reduced)
        # Status flow: pending -> confirmed (after payment) -> completed (after fulfillment)
        if order.status == 'confirmed':
            # Stock has already been reduced when payment was confirmed
            # Just mark order as completed (fulfilled by admin)
            order.status = 'completed'
            db.session.commit()
            flash(f'Order #{order_id} marked as completed!', 'success')
        elif order.status == 'pending':
            # This shouldn't happen in normal flow, but handle it gracefully
            flash(f'Order #{order_id} is still pending payment. Please wait for payment confirmation.', 'warning')
        elif order.status == 'completed':
            flash(f'Order #{order_id} is already completed!', 'info')
        else:
            flash(f'Order #{order_id} has an unknown status: {order.status}', 'warning')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating order: {str(e)}', 'danger')
        print(f"Error updating order {order_id}: {e}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reports')
@login_required
def admin_reports():
    try:
<<<<<<< HEAD
        orders = Order.query.order_by(Order.date.desc()).all()
        total_orders = Order.query.count()
        completed_orders = Order.query.filter_by(status='completed').count()
        pending_orders = Order.query.filter_by(status='pending').count()
        total_revenue = sum(order.total for order in orders)
    except Exception as e:
        print(f"Database error: {e}")
        orders = []
        total_orders = 0
        completed_orders = 0
        pending_orders = 0
        total_revenue = 0
    
    return render_template('admin_reports.html', 
                         orders=orders,
                         total_orders=total_orders,
                         completed_orders=completed_orders,
                         pending_orders=pending_orders,
                         total_revenue=total_revenue)
=======
        total_orders = Order.query.count()
        completed_orders = Order.query.filter_by(status='completed').count()
        pending_orders = Order.query.filter_by(status='pending').count()
        total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0
        total_customers = len({(order.customer_name, order.phone, order.email) for order in Order.query.all()})
        recent_orders = Order.query.order_by(Order.date.desc()).limit(10).all()
    except Exception as e:
        print(f"Database error: {e}")
        total_orders = completed_orders = pending_orders = total_revenue = total_customers = 0
        recent_orders = []

    return render_template('admin_reports.html',
                           total_orders=total_orders,
                           completed_orders=completed_orders,
                           pending_orders=pending_orders,
                           total_revenue=total_revenue,
                           total_customers=total_customers,
                           recent_orders=recent_orders)
>>>>>>> f0cf3aaebcdfadd57343fa47bc5a5c138a69e28b

@app.route('/admin/customers')
@login_required
def admin_customers():
    try:
        orders = Order.query.order_by(Order.date.desc()).all()
<<<<<<< HEAD
        customers = {}
        for order in orders:
            if order.customer_name not in customers:
                customers[order.customer_name] = {
                    'name': order.customer_name,
                    'phone': order.phone,
                    'email': order.email,
                    'address': order.address,
                    'total_orders': 0,
                    'total_spent': 0
                }
            customers[order.customer_name]['total_orders'] += 1
            customers[order.customer_name]['total_spent'] += order.total
        
        customer_list = list(customers.values())
    except Exception as e:
        print(f"Database error: {e}")
        customer_list = []
    
    return render_template('admin_customers.html', customers=customer_list)
=======
        unique_customers = {}
        for order in orders:
            key = (order.customer_name, order.phone, order.email)
            if key not in unique_customers:
                unique_customers[key] = {
                    'name': order.customer_name,
                    'phone': order.phone,
                    'email': order.email,
                    'orders': 0,
                    'last_order': order.date
                }
            unique_customers[key]['orders'] += 1
            if order.date > unique_customers[key]['last_order']:
                unique_customers[key]['last_order'] = order.date
    except Exception as e:
        print(f"Database error: {e}")
        unique_customers = {}

    return render_template('admin_customers.html', customers=unique_customers.values())
>>>>>>> f0cf3aaebcdfadd57343fa47bc5a5c138a69e28b

@app.route('/admin/images')
@login_required
def admin_images():
    images = {
        'bhooswarga': 'bhooswarga_garden.png',
        'dr_sumaraj': 'dr_sumaraj.png',
        'byre_gowda': 'byre_gowda.png',
        'vishwadeep_k': 'vishwadeep_k.jpg',
        'abhishek_r': 'abhishek_r.jpg'
    }
    return render_template('admin_images.html', images=images)

@app.route('/admin/upload_image', methods=['POST'])
@login_required
def upload_image():
    target = request.form.get('target')
    file = request.files.get('image')

    allowed_targets = {
        'bhooswarga': 'bhooswarga_garden.png',
        'dr_sumaraj': 'dr_sumaraj.png',
        'byre_gowda': 'byre_gowda.png',
        'vishwadeep_k': 'vishwadeep_k.jpg',
        'abhishek_r': 'abhishek_r.jpg'
    }

    if target not in allowed_targets:
        flash('Invalid image target.', 'error')
        return redirect(url_for('admin_images'))

    if not file or file.filename == '':
        flash('No image selected.', 'error')
        return redirect(url_for('admin_images'))

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    if ext not in {'.png', '.jpg', '.jpeg', '.gif'}:
        flash('Unsupported image format. Use PNG/JPG/GIF.', 'error')
        return redirect(url_for('admin_images'))

    save_name = allowed_targets[target]
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], save_name)
    file.save(save_path)

    flash(f'Updated image for {target}.', 'success')
    return redirect(url_for('admin_images'))

<<<<<<< HEAD
@app.route('/admin/mark_notification_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    try:
        notification = Notification.query.get_or_404(notification_id)
        notification.is_read = True
        db.session.commit()
        flash('Notification marked as read', 'success')
    except Exception as e:
        flash(f'Error updating notification: {e}', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/notifications')
@login_required
def admin_notifications():
    all_notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    return render_template('admin_notifications.html', notifications=all_notifications)

@app.route('/admin/change_username', methods=['POST'])
@login_required
def admin_change_username():
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_username = data.get('new_username', '').strip()

    if not current_password or not new_username:
        return jsonify({'success': False, 'error': 'All fields are required'})

    admin = Admin.query.get(current_user.id)
    if not admin or not admin.check_password(current_password):
        return jsonify({'success': False, 'error': 'Incorrect password'})

    if Admin.query.filter_by(username=new_username).first():
        return jsonify({'success': False, 'error': 'Username already taken'})

    admin.username = new_username
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/db-check')
@login_required
def db_check():
    """Diagnostic endpoint to check database status"""
    ensure_db_initialized()
    
    try:
        db.session.expire_all()
        
        vegetables_count = Vegetable.query.count()
        orders_count = Order.query.count()
        feedbacks_count = Feedback.query.count()
        admins_count = Admin.query.count()
        notifications_count = Notification.query.count()
        
        vegetables = Vegetable.query.all()
        orders = Order.query.order_by(Order.date.desc()).limit(10).all()
        
        status = {
            'database': 'Connected ✓',
            'vegetables': vegetables_count,
            'orders': orders_count,
            'feedbacks': feedbacks_count,
            'admins': admins_count,
            'notifications': notifications_count,
            'vegetables_list': [
                {'id': v.id, 'name': v.name, 'price': v.price, 'stock': v.stock}
                for v in vegetables[:5]
            ],
            'recent_orders': [
                {
                    'id': o.id,
                    'customer': o.customer_name,
                    'total': o.total,
                    'status': o.status,
                    'date': o.date.strftime('%Y-%m-%d %H:%M:%S') if o.date else None
                }
                for o in orders
            ]
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({
            'database': 'Error',
            'error': str(e),
            'type': type(e).__name__
        }), 500

@app.route('/admin/reseed-database')
@login_required
def reseed_database():
    """Reseed the database with sample data"""
    try:
        ensure_db_initialized()
        
        # Seed vegetables if empty or needs refresh
        seed_data = [
            {'name': 'Tomatoes', 'price': 40.0, 'stock': 50, 'description': 'Fresh red tomatoes from our farm'},
            {'name': 'Potatoes', 'price': 30.0, 'stock': 100, 'description': 'High quality potatoes'},
            {'name': 'Onions', 'price': 35.0, 'stock': 75, 'description': 'Fresh onions'},
            {'name': 'Carrots', 'price': 45.0, 'stock': 60, 'description': 'Sweet and crunchy carrots'},
            {'name': 'Spinach', 'price': 25.0, 'stock': 40, 'description': 'Fresh green spinach'},
            {'name': 'Broccoli', 'price': 60.0, 'stock': 30, 'description': 'Organic broccoli'},
            {'name': 'Bell Peppers', 'price': 55.0, 'stock': 45, 'description': 'Colorful bell peppers'},
            {'name': 'Cucumbers', 'price': 35.0, 'stock': 55, 'description': 'Fresh cucumbers'},
            {'name': 'Cabbage', 'price': 28.0, 'stock': 35, 'description': 'Green cabbage'},
            {'name': 'Cauliflower', 'price': 50.0, 'stock': 25, 'description': 'Fresh cauliflower'}
        ]
        
        # Check existing vegetables
        existing_count = Vegetable.query.count()
        
        if existing_count == 0:
            for data in seed_data:
                vegetable = Vegetable(**data)
                db.session.add(vegetable)
            db.session.commit()
            print(f"✅ Seeded {len(seed_data)} vegetables")
            flash(f'✅ Database seeded with {len(seed_data)} vegetables', 'success')
        else:
            flash(f'Database already has {existing_count} vegetables. No seeding needed.', 'info')
        
        return redirect(url_for('admin_dashboard'))
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        flash(f'Error seeding database: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

# Make the function available at module level
=======

>>>>>>> f0cf3aaebcdfadd57343fa47bc5a5c138a69e28b
def create_tables_and_seed():
    with app.app_context():
        db.create_all()
        ensure_feedback_rating_column()
        
        # Do not create a default admin automatically for security reasons.
        # Admin users should be created explicitly using a database tool or migration.
        
        # Update image filenames for existing vegetables if missing
        image_map = {'Tomatoes': 'tomato.jpeg', 'Brinjal': 'brinjal.jpeg', 'Cauliflower': 'brinjal.jpeg'}
        for veg_name, img_file in image_map.items():
            veg = Vegetable.query.filter_by(name=veg_name).first()
            if veg:
                veg.image = img_file
                print(f"Updated image for {veg_name}: {img_file}")
        db.session.commit()
        print("Image migration complete")

        # Seed data if database is empty
        if Vegetable.query.count() == 0:
            seed_data = [
                {'name': 'Tomatoes', 'price': 40.0, 'stock': 50, 'image': 'tomato.jpeg', 'description': 'Fresh red tomatoes from our farm'},
                {'name': 'Potatoes', 'price': 30.0, 'stock': 100, 'image': None, 'description': 'High quality potatoes'},
                {'name': 'Onions', 'price': 35.0, 'stock': 75, 'image': None, 'description': 'Fresh onions'},
                {'name': 'Carrots', 'price': 45.0, 'stock': 60, 'image': None, 'description': 'Sweet and crunchy carrots'},
                {'name': 'Spinach', 'price': 25.0, 'stock': 40, 'image': None, 'description': 'Fresh green spinach'},
                {'name': 'Broccoli', 'price': 60.0, 'stock': 30, 'image': None, 'description': 'Organic broccoli'},
                {'name': 'Bell Peppers', 'price': 55.0, 'stock': 45, 'image': None, 'description': 'Colorful bell peppers'},
                {'name': 'Cucumbers', 'price': 35.0, 'stock': 55, 'image': None, 'description': 'Fresh cucumbers'},
                {'name': 'Cabbage', 'price': 28.0, 'stock': 35, 'image': None, 'description': 'Green cabbage'},
                {'name': 'Brinjal', 'price': 50.0, 'stock': 25, 'image': 'brinjal.jpeg', 'description': 'Fresh brinjal'}
            ]
            
            for data in seed_data:
                vegetable = Vegetable(**data)
                db.session.add(vegetable)
            
            db.session.commit()
            print("Database seeded with sample vegetables!")

# ==================== CUSTOMER FEATURES ====================

# Advanced Search & Filter API
@app.route('/api/search')
def api_search():
    query = request.args.get('q', '').lower()
    sort_by = request.args.get('sort', 'name')
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)
    
    vegetables = Vegetable.query.filter(Vegetable.stock > 0)
    
    # Apply search filter
    if query:
        vegetables = vegetables.filter(Vegetable.name.ilike(f'%{query}%'))
    
    # Apply price filter
    if price_min is not None:
        vegetables = vegetables.filter(Vegetable.price >= price_min)
    if price_max is not None:
        vegetables = vegetables.filter(Vegetable.price <= price_max)
    
    # Apply sorting
    if sort_by == 'price_low':
        vegetables = vegetables.order_by(Vegetable.price.asc())
    elif sort_by == 'price_high':
        vegetables = vegetables.order_by(Vegetable.price.desc())
    else:
        vegetables = vegetables.order_by(Vegetable.name.asc())
    
    return jsonify({
        'vegetables': [veg.to_dict() for veg in vegetables.all()]
    })

# ==================== ADMIN ANALYTICS ====================

@app.route('/admin/analytics')
@login_required
def admin_analytics():
    """Advanced analytics dashboard"""
    try:
        import json
        from datetime import datetime, timedelta
        
        # Sales Analytics
        orders = Order.query.all()
        
        # Calculate key metrics
        total_revenue = sum(order.total for order in orders)
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o.status == 'completed'])
        pending_orders = len([o for o in orders if o.status == 'pending'])
        
        # Payment method breakdown
        payment_methods = {}
        for order in orders:
            method = order.payment_method or 'cod'
            payment_methods[method] = payment_methods.get(method, 0) + 1
        
        # Best selling products
        product_sales = {}
        for order in orders:
            for item in order.order_items:
                if item.vegetable.name not in product_sales:
                    product_sales[item.vegetable.name] = {'qty': 0, 'revenue': 0}
                product_sales[item.vegetable.name]['qty'] += item.quantity
                product_sales[item.vegetable.name]['revenue'] += item.price * item.quantity
        
        sorted_products = sorted(product_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)[:5]
        
        # Customer Analytics
        customers = {}
        for order in orders:
            key = order.phone
            if key not in customers:
                customers[key] = {
                    'name': order.customer_name,
                    'phone': order.phone,
                    'email': order.email,
                    'orders': 0,
                    'total_spent': 0,
                    'first_order': order.date
                }
            customers[key]['orders'] += 1
            customers[key]['total_spent'] += order.total
            customers[key]['last_order'] = order.date
        
        repeat_customers = len([c for c in customers.values() if c['orders'] > 1])
        
        # Daily revenue (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_orders = [o for o in orders if o.date >= thirty_days_ago]
        
        daily_revenue = {}
        for order in recent_orders:
            date_key = order.date.strftime('%Y-%m-%d')
            daily_revenue[date_key] = daily_revenue.get(date_key, 0) + order.total
        
        # Stock status
        vegetables = Vegetable.query.all()
        low_stock = [v for v in vegetables if v.stock < 20]
        out_of_stock = [v for v in vegetables if v.stock == 0]
        
        analytics = {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'repeat_customers': repeat_customers,
            'total_customers': len(customers),
            'avg_order_value': total_revenue / total_orders if total_orders > 0 else 0,
            'payment_methods': payment_methods,
            'top_products': sorted_products,
            'low_stock_items': len(low_stock),
            'out_of_stock_items': len(out_of_stock),
            'daily_revenue': daily_revenue
        }
        
    except Exception as e:
        flash(f'Error loading analytics: {e}', 'error')
        analytics = {}
    
    return render_template('admin_analytics.html', analytics=analytics)

@app.route('/admin/api/sales-chart')
@login_required
def api_sales_chart():
    """API endpoint for sales chart data"""
    try:
        from datetime import datetime, timedelta
        
        # Get daily data for last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        orders = Order.query.filter(Order.date >= thirty_days_ago).all()
        
        daily_data = {}
        for order in orders:
            date_key = order.date.strftime('%Y-%m-%d')
            if date_key not in daily_data:
                daily_data[date_key] = {'orders': 0, 'revenue': 0}
            daily_data[date_key]['orders'] += 1
            daily_data[date_key]['revenue'] += order.total
        
        # Fill missing dates with 0
        current_date = datetime.utcnow().date() - timedelta(days=30)
        while current_date <= datetime.utcnow().date():
            date_key = current_date.strftime('%Y-%m-%d')
            if date_key not in daily_data:
                daily_data[date_key] = {'orders': 0, 'revenue': 0}
            current_date += timedelta(days=1)
        
        return jsonify({
            'dates': sorted(daily_data.keys()),
            'orders': [daily_data[d]['orders'] for d in sorted(daily_data.keys())],
            'revenue': [daily_data[d]['revenue'] for d in sorted(daily_data.keys())]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/product-chart')
@login_required
def api_product_chart():
    """API endpoint for product sales chart"""
    try:
        orders = Order.query.all()
        product_sales = {}
        
        for order in orders:
            for item in order.order_items:
                name = item.vegetable.name
                if name not in product_sales:
                    product_sales[name] = 0
                product_sales[name] += item.quantity
        
        sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return jsonify({
            'products': [p[0] for p in sorted_products],
            'quantities': [p[1] for p in sorted_products]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/inventory-management')
@login_required
def inventory_management():
    """Inventory management with stock awareness"""
    try:
        vegetables = Vegetable.query.all()
        
        # Categorize items
        in_stock = [v for v in vegetables if v.stock > 20]
        low_stock = [v for v in vegetables if 0 < v.stock <= 20]
        out_of_stock = [v for v in vegetables if v.stock == 0]
        
        inventory_data = {
            'in_stock': in_stock,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
            'total_items': len(vegetables),
            'alert_items': len(low_stock) + len(out_of_stock)
        }
    except Exception as e:
        flash(f'Error loading inventory: {e}', 'error')
        inventory_data = {'in_stock': [], 'low_stock': [], 'out_of_stock': []}
    
    return render_template('admin_inventory.html', inventory=inventory_data)

def init_db():
    """Initialize database with seed data"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Check if admin exists
            admin = Admin.query.filter_by(email='admin@gmail.com').first()
            if not admin:
                admin = Admin(
                    email='admin@gmail.com',
                    password_hash=generate_password_hash('admin123')
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created: admin@gmail.com / admin123")
            
            # Check if vegetables exist
            if Vegetable.query.count() == 0:
                vegetables = [
                    Vegetable(name='Tomatoes', description='Fresh red tomatoes from our farm', price=40, stock=50),
                    Vegetable(name='Potatoes', description='High quality potatoes', price=30, stock=75),
                    Vegetable(name='Onions', description='Fresh onions', price=35, stock=60),
                    Vegetable(name='Carrots', description='Fresh orange carrots', price=25, stock=45),
                    Vegetable(name='Cucumber', description='Fresh cucumber', price=20, stock=40),
                    Vegetable(name='Capsicum', description='Fresh capsicum', price=45, stock=35),
                    Vegetable(name='Broccoli', description='Fresh broccoli', price=50, stock=30),
                    Vegetable(name='Spinach', description='Fresh spinach leaves', price=15, stock=55),
                    Vegetable(name='Cabbage', description='Fresh cabbage', price=20, stock=50),
                    Vegetable(name='Lettuce', description='Fresh lettuce', price=25, stock=40),
                ]
                for veg in vegetables:
                    db.session.add(veg)
                db.session.commit()
                print(f"✅ {len(vegetables)} vegetables added to database")
            
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"⚠️ Database initialization error: {e}")
app = create_app()

if __name__ == '__main__':
    create_tables_and_seed()
    app.run(debug=True, host='127.0.0.1', port=8080)
   
