from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os, json, secrets, string

app = Flask(__name__)
app.secret_key = "ffpanels_super_secret_2026"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ffpanels.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

db = SQLAlchemy(app)

ADMIN_USERNAME = "narutopannel"
ADMIN_PASSWORD = "narrutocodexx"
BINANCE_ID = "1085856438"
UPI_ID = "suman168@fam"

# ─── MODELS ────────────────────────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)
    payments = db.relationship('PaymentRequest', backref='user', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    tags = db.Column(db.Text, default='[]')
    features = db.Column(db.Text, default='[]')
    notice = db.Column(db.String(500), default='')
    video_path = db.Column(db.String(500), default='')
    apk_link = db.Column(db.String(500), default='')
    plans = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    key_stocks = db.relationship('KeyStock', backref='category', lazy=True)
    key_requests = db.relationship('KeyRequest', backref='category', lazy=True)
    def get_tags(self): return json.loads(self.tags)
    def get_features(self): return json.loads(self.features)
    def get_plans(self): return json.loads(self.plans)

class KeyStock(db.Model):
    """Pre-loaded keys for a specific plan in a category"""
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    plan_label = db.Column(db.String(100))
    plan_price = db.Column(db.Float)
    key_code = db.Column(db.String(200), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    used_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class KeyRequest(db.Model):
    """When no key in stock, user request is stored here"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    cat_name = db.Column(db.String(200))
    plan_label = db.Column(db.String(100))
    plan_price = db.Column(db.Float)
    key_code = db.Column(db.String(200), default='')
    status = db.Column(db.String(20), default='pending')  # pending / fulfilled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='key_requests')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cat_name = db.Column(db.String(200))
    plan_label = db.Column(db.String(100))
    price = db.Column(db.Float)
    key_code = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Delivered')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PaymentRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    method = db.Column(db.String(20))
    amount = db.Column(db.Float)
    txn_id = db.Column(db.String(200))
    screenshot_path = db.Column(db.String(500), default='')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ─── HELPERS ───────────────────────────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def d(*a, **kw):
        if 'user_id' not in session: return redirect(url_for('login'))
        return f(*a, **kw)
    return d

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def d(*a, **kw):
        if not session.get('is_admin'): return redirect(url_for('login'))
        return f(*a, **kw)
    return d

def seed_data():
    if Category.query.count() == 0:
        cats = [
            Category(name="BIGBULL CHEATS INJECTOR", tags=json.dumps(["Non Root","Android","User"]),
                features=json.dumps(["Silent Aim","Aimbot","Auto Fire","ESP"]),
                notice="ONCE CHECK UPDATE BEFORE BUY",
                plans=json.dumps([{"label":"12 Hours Free","price":0},{"label":"3 Days Safe","price":199},{"label":"7 Days Standard","price":329},{"label":"30 Days Standard","price":799}])),
            Category(name="PATO TEAM FF", tags=json.dumps(["Non Root","Android","User"]),
                features=json.dumps(["Silent Aim","Aim Magnet","Speed"]),
                notice="WAIT FOR NEW UPDATE CHECK IN TG",
                plans=json.dumps([{"label":"3 Days Safe","price":199},{"label":"7 Days Standard","price":329},{"label":"15 Days Standard","price":649},{"label":"30 Days Standard","price":799}])),
        ]
        for c in cats: db.session.add(c)
        db.session.commit()

# ─── AUTH ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if session.get('is_admin'): return redirect(url_for('admin_dashboard'))
    if 'user_id' in session: return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username','').strip()
        p = request.form.get('password','').strip()
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            session['is_admin'] = True; session.permanent = True
            return redirect(url_for('admin_dashboard'))
        user = User.query.filter_by(username=u).first()
        if user and check_password_hash(user.password, p):
            session['user_id'] = user.id; session.permanent = True
            return redirect(url_for('home'))
        flash('Invalid username or password','error')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form.get('username','').strip()
        e = request.form.get('email','').strip()
        p = request.form.get('password','').strip()
        c = request.form.get('confirm_password','').strip()
        if not all([u,e,p]): flash('All fields required','error'); return render_template('register.html')
        if p != c: flash('Passwords do not match','error'); return render_template('register.html')
        if len(p) < 6: flash('Password min 6 characters','error'); return render_template('register.html')
        if User.query.filter_by(username=u).first(): flash('Username already taken','error'); return render_template('register.html')
        if User.query.filter_by(email=e).first(): flash('Email already registered','error'); return render_template('register.html')
        db.session.add(User(username=u, email=e, password=generate_password_hash(p)))
        db.session.commit()
        flash('Account created! Please login.','success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

# ─── USER PAGES ────────────────────────────────────────────────────────────

@app.route('/home')
@login_required
def home():
    user = User.query.get(session['user_id'])
    if user is None:
        session.clear()
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('login'))
    today = Order.query.filter_by(user_id=user.id).filter(db.func.date(Order.created_at)==datetime.utcnow().date()).count()
    total = Order.query.filter_by(user_id=user.id).count()
    return render_template('home.html', user=user, today_orders=today, total_orders=total)

@app.route('/store')
@login_required
def store():
    user = User.query.get(session['user_id'])
    if user is None:
        session.clear()
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('login'))
    cats = Category.query.order_by(Category.created_at.desc()).all()
    # Stock count per cat per plan
    stock_info = {}
    for cat in cats:
        stock_info[cat.id] = {}
        for plan in cat.get_plans():
            count = KeyStock.query.filter_by(category_id=cat.id, plan_label=plan['label'], is_used=False).count()
            stock_info[cat.id][plan['label']] = count
    return render_template('store.html', user=user, categories=cats, stock_info=stock_info)

@app.route('/buy/<int:cat_id>', methods=['POST'])
@login_required
def buy_key(cat_id):
    user = User.query.get(session['user_id'])
    if user is None:
        session.clear()
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('login'))
    cat = Category.query.get_or_404(cat_id)
    idx = int(request.form.get('plan_idx', 0))
    plans = cat.get_plans()
    if idx >= len(plans): flash('Invalid plan','error'); return redirect(url_for('store'))
    plan = plans[idx]
    price = float(plan['price'])
    if price > 0 and user.balance < price:
        flash('⚠️ Insufficient balance! Please add money.','error')
        return redirect(url_for('store'))
    # Deduct balance
    if price > 0: user.balance -= price
    # Try to get key from stock
    stock = KeyStock.query.filter_by(category_id=cat_id, plan_label=plan['label'], is_used=False).first()
    if stock:
        stock.is_used = True
        stock.used_by = user.id
        key = stock.key_code
        db.session.add(Order(user_id=user.id, cat_name=cat.name, plan_label=plan['label'], price=price, key_code=key, status='Delivered'))
        db.session.commit()
        flash(f'✅ Key Delivered! Your key: {key}','success')
        return redirect(url_for('my_keys'))
    else:
        # No stock - create key request
        db.session.add(KeyRequest(user_id=user.id, category_id=cat_id, cat_name=cat.name,
                                   plan_label=plan['label'], plan_price=price, status='pending'))
        db.session.commit()
        flash('⏳ No key in stock! Request sent to admin. You will receive your key soon.','success')
        return redirect(url_for('my_keys'))

@app.route('/keys')
@login_required
def my_keys():
    user = User.query.get(session['user_id'])
    if user is None:
        session.clear()
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('login'))
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    key_reqs = KeyRequest.query.filter_by(user_id=user.id).order_by(KeyRequest.created_at.desc()).all()
    delivered = sum(1 for o in orders if o.status=='Delivered')
    pending = sum(1 for r in key_reqs if r.status=='pending')
    return render_template('keys.html', user=user, orders=orders, key_reqs=key_reqs, delivered=delivered, pending=pending)

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if user is None:
        session.clear()
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        np = request.form.get('new_password','').strip()
        cp = request.form.get('confirm_password','').strip()
        if np and np == cp and len(np) >= 6:
            user.password = generate_password_hash(np); db.session.commit()
            flash('Password updated!','success')
        else:
            flash('Passwords do not match or too short','error')
    return render_template('profile.html', user=user)

@app.route('/add-money', methods=['GET','POST'])
@login_required
def add_money():
    user = User.query.get(session['user_id'])
    if user is None:
        session.clear()
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        method = request.form.get('method','upi')
        amount = request.form.get('amount','').strip()
        txn_id = request.form.get('txn_id','').strip()
        if not amount or not txn_id:
            flash('Amount and Transaction ID required','error')
            return render_template('add_money.html', user=user, BINANCE_ID=BINANCE_ID, UPI_ID=UPI_ID)
        try: amount = float(amount)
        except: flash('Invalid amount','error'); return render_template('add_money.html', user=user, BINANCE_ID=BINANCE_ID, UPI_ID=UPI_ID)
        if amount <= 0: flash('Amount must be > 0','error'); return render_template('add_money.html', user=user, BINANCE_ID=BINANCE_ID, UPI_ID=UPI_ID)
        ss_path = ''
        if 'screenshot' in request.files:
            f = request.files['screenshot']
            if f.filename:
                fn = secure_filename(f'pay_{user.id}_{int(datetime.utcnow().timestamp())}_{f.filename}')
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                ss_path = fn
        db.session.add(PaymentRequest(user_id=user.id, method=method, amount=amount, txn_id=txn_id, screenshot_path=ss_path))
        db.session.commit()
        flash('✅ Payment request submitted! Admin will verify and add balance soon.','success')
        return redirect(url_for('home'))
    return render_template('add_money.html', user=user, BINANCE_ID=BINANCE_ID, UPI_ID=UPI_ID)

# ─── ADMIN ─────────────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html',
        users_count=User.query.count(),
        cats_count=Category.query.count(),
        orders_count=Order.query.count(),
        pending_payments=PaymentRequest.query.filter_by(status='pending').count(),
        pending_keys=KeyRequest.query.filter_by(status='pending').count(),
        total_revenue=db.session.query(db.func.sum(Order.price)).scalar() or 0,
        recent_orders=Order.query.order_by(Order.created_at.desc()).limit(8).all()
    )

@app.route('/admin/categories')
@admin_required
def admin_categories():
    cats = Category.query.order_by(Category.created_at.desc()).all()
    stock_counts = {}
    for cat in cats:
        stock_counts[cat.id] = KeyStock.query.filter_by(category_id=cat.id, is_used=False).count()
    return render_template('admin/categories.html', categories=cats, stock_counts=stock_counts)

@app.route('/admin/categories/add', methods=['GET','POST'])
@admin_required
def admin_add_category():
    if request.method == 'POST':
        features = [f.strip() for f in request.form.get('features','').split('\n') if f.strip()]
        labels = request.form.getlist('plan_label')
        prices = request.form.getlist('plan_price')
        plans = [{"label":l,"price":float(p or 0)} for l,p in zip(labels,prices) if l.strip()]
        video_path = ''
        if 'video' in request.files:
            v = request.files['video']
            if v.filename:
                fn = secure_filename(v.filename)
                v.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                video_path = fn
        db.session.add(Category(name=request.form.get('name'), notice=request.form.get('notice',''),
            tags=json.dumps(request.form.getlist('tags')),
            features=json.dumps(features), plans=json.dumps(plans), video_path=video_path))
        db.session.commit()
        flash('Category added!','success')
        return redirect(url_for('admin_categories'))
    return render_template('admin/category_form.html', cat=None)

@app.route('/admin/categories/edit/<int:cid>', methods=['GET','POST'])
@admin_required
def admin_edit_category(cid):
    cat = Category.query.get_or_404(cid)
    if request.method == 'POST':
        cat.name = request.form.get('name')
        cat.notice = request.form.get('notice','')
        cat.apk_link = request.form.get('apk_link','')
        cat.tags = json.dumps(request.form.getlist('tags'))
        cat.features = json.dumps([f.strip() for f in request.form.get('features','').split('\n') if f.strip()])
        labels = request.form.getlist('plan_label')
        prices = request.form.getlist('plan_price')
        cat.plans = json.dumps([{"label":l,"price":float(p or 0)} for l,p in zip(labels,prices) if l.strip()])
        if 'video' in request.files:
            v = request.files['video']
            if v.filename:
                fn = secure_filename(v.filename); v.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                cat.video_path = fn
        db.session.commit()
        flash('Category updated!','success')
        return redirect(url_for('admin_categories'))
    return render_template('admin/category_form.html', cat=cat)

@app.route('/admin/categories/delete/<int:cid>', methods=['POST'])
@admin_required
def admin_delete_category(cid):
    cat = Category.query.get_or_404(cid)
    KeyStock.query.filter_by(category_id=cid).delete()
    KeyRequest.query.filter_by(category_id=cid).delete()
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted!','success')
    return redirect(url_for('admin_categories'))

# KEY STOCK MANAGEMENT
@app.route('/admin/keys/<int:cat_id>')
@admin_required
def admin_keys(cat_id):
    cat = Category.query.get_or_404(cat_id)
    stocks = KeyStock.query.filter_by(category_id=cat_id).order_by(KeyStock.created_at.desc()).all()
    return render_template('admin/keys.html', cat=cat, stocks=stocks)

@app.route('/admin/keys/<int:cat_id>/add', methods=['POST'])
@admin_required
def admin_add_keys(cat_id):
    cat = Category.query.get_or_404(cat_id)
    plan_label = request.form.get('plan_label')
    plan_price = float(request.form.get('plan_price', 0))
    keys_raw = request.form.get('keys_text','').strip()
    keys_list = [k.strip() for k in keys_raw.split('\n') if k.strip()]
    count = 0
    for key in keys_list:
        db.session.add(KeyStock(category_id=cat_id, plan_label=plan_label, plan_price=plan_price, key_code=key))
        count += 1
    db.session.commit()
    flash(f'✅ {count} key(s) added for "{plan_label}"!','success')
    return redirect(url_for('admin_keys', cat_id=cat_id))

@app.route('/admin/keys/delete/<int:kid>', methods=['POST'])
@admin_required
def admin_delete_key(kid):
    k = KeyStock.query.get_or_404(kid)
    cat_id = k.category_id
    db.session.delete(k)
    db.session.commit()
    flash('Key deleted','success')
    return redirect(url_for('admin_keys', cat_id=cat_id))

# KEY REQUESTS
@app.route('/admin/key-requests')
@admin_required
def admin_key_requests():
    reqs = KeyRequest.query.order_by(KeyRequest.created_at.desc()).all()
    return render_template('admin/key_requests.html', reqs=reqs)

@app.route('/admin/key-requests/fulfill/<int:rid>', methods=['POST'])
@admin_required
def admin_fulfill_key(rid):
    req = KeyRequest.query.get_or_404(rid)
    key_code = request.form.get('key_code','').strip()
    if not key_code:
        flash('Key code required!','error')
        return redirect(url_for('admin_key_requests'))
    req.key_code = key_code
    req.status = 'fulfilled'
    # Add order for user
    db.session.add(Order(user_id=req.user_id, cat_name=req.cat_name, plan_label=req.plan_label,
                          price=req.plan_price, key_code=key_code, status='Delivered'))
    db.session.commit()
    flash(f'✅ Key delivered to {req.user.username}!','success')
    return redirect(url_for('admin_key_requests'))

@app.route('/admin/users')
@admin_required
def admin_users():
    return render_template('admin/users.html', users=User.query.order_by(User.created_at.desc()).all())

@app.route('/admin/users/balance/<int:uid>', methods=['POST'])
@admin_required
def admin_update_balance(uid):
    user = User.query.get_or_404(uid)
    action = request.form.get('action')
    amount = float(request.form.get('amount',0))
    if action == 'add': user.balance += amount
    elif action == 'remove': user.balance = max(0, user.balance - amount)
    elif action == 'set': user.balance = amount
    db.session.commit()
    flash(f'Balance updated for {user.username}','success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:uid>', methods=['POST'])
@admin_required
def admin_delete_user(uid):
    user = User.query.get_or_404(uid)
    Order.query.filter_by(user_id=uid).delete()
    PaymentRequest.query.filter_by(user_id=uid).delete()
    KeyRequest.query.filter_by(user_id=uid).delete()
    db.session.delete(user)
    db.session.commit()
    flash('User deleted!','success')
    return redirect(url_for('admin_users'))

@app.route('/admin/payments')
@admin_required
def admin_payments():
    return render_template('admin/payments.html', payments=PaymentRequest.query.order_by(PaymentRequest.created_at.desc()).all())

@app.route('/admin/payments/action/<int:pid>', methods=['POST'])
@admin_required
def admin_payment_action(pid):
    pay = PaymentRequest.query.get_or_404(pid)
    action = request.form.get('action')
    if action == 'approve' and pay.status == 'pending':
        pay.status = 'approved'; pay.user.balance += pay.amount
        flash(f'✅ Approved! ₹{pay.amount:.0f} added to {pay.user.username}','success')
    elif action == 'reject' and pay.status == 'pending':
        pay.status = 'rejected'
        flash(f'❌ Payment rejected for {pay.user.username}','success')
    db.session.commit()
    return redirect(url_for('admin_payments'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    return render_template('admin/orders.html', orders=Order.query.order_by(Order.created_at.desc()).all())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, host='0.0.0.0', port=5000)

# Inject pending_keys count into all admin templates
@app.context_processor
def inject_pending():
    if session.get('is_admin'):
        return dict(
            pending_keys=KeyRequest.query.filter_by(status='pending').count(),
            pending_payments=PaymentRequest.query.filter_by(status='pending').count()
        )
    return {}
