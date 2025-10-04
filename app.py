from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
import secrets


# Email functionality removed for simplicity
import json

app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))

# Database configuration for production (PostgreSQL) and development (SQLite)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Production: PostgreSQL on Render
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Development: SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "banking.db")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # customer, staff, admin
    phone = db.Column(db.String(15), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 2FA fields
    otp_secret = db.Column(db.String(32))
    otp_verified = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None
        }

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_number = db.Column(db.String(12), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    kyc_verified = db.Column(db.Boolean, default=False)
    account_status = db.Column(db.String(20), default='pending')  # pending, active, suspended, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # KYC fields
    pan_number = db.Column(db.String(10))
    aadhar_number = db.Column(db.String(12))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    
    user = db.relationship('User', backref='customer_profile')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_number': self.account_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'balance': self.balance,
            'account_status': self.account_status,
            'kyc_verified': self.kyc_verified,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdraw, transfer
    amount = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    related_customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))  # For transfers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', foreign_keys=[customer_id])
    related_customer = db.relationship('Customer', foreign_keys=[related_customer_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'balance_after': self.balance_after,
            'description': self.description,
            'related_customer_id': self.related_customer_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    loan_type = db.Column(db.String(50), nullable=False)  # personal, home, car, business
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    tenure_months = db.Column(db.Integer, nullable=False)
    emi_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, active, closed
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    customer = db.relationship('Customer')
    approver = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'loan_type': self.loan_type,
            'amount': self.amount,
            'interest_rate': self.interest_rate,
            'tenure_months': self.tenure_months,
            'emi_amount': self.emi_amount,
            'status': self.status,
            'applied_at': self.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
            'approved_at': self.approved_at.strftime('%Y-%m-%d %H:%M:%S') if self.approved_at else None
        }

class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    deposit_type = db.Column(db.String(20), nullable=False)  # fixed, recurring
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    tenure_months = db.Column(db.Integer, nullable=False)
    maturity_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, matured, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    maturity_date = db.Column(db.DateTime)
    
    customer = db.relationship('Customer')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'deposit_type': self.deposit_type,
            'amount': self.amount,
            'interest_rate': self.interest_rate,
            'tenure_months': self.tenure_months,
            'maturity_amount': self.maturity_amount,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'maturity_date': self.maturity_date.strftime('%Y-%m-%d') if self.maturity_date else None
        }

class FraudAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # large_withdrawal, unusual_transaction, multiple_failed_attempts
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='open')  # open, investigating, resolved, false_positive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    customer = db.relationship('Customer')
    resolver = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'alert_type': self.alert_type,
            'description': self.description,
            'severity': self.severity,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'resolved_at': self.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if self.resolved_at else None
        }

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # customer = db.relationship('Customer', backref='contact_messages', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
# Utility Functions
def generate_otp():
    return str(secrets.randbelow(900000) + 100000)

def send_otp_email(email, otp):
    # Simulate OTP sending (in production, use actual email service)
    print(f"OTP for {email}: {otp}")
    return True

def check_fraud_conditions(customer_id, amount, transaction_type):
    """Check for potential fraud conditions"""
    customer = Customer.query.get(customer_id)
    
    # Large withdrawal alert (more than 50% of balance)
    if transaction_type == 'withdraw' and amount > customer.balance * 0.5:
        alert = FraudAlert(
            customer_id=customer_id,
            alert_type='large_withdrawal',
            description=f'Large withdrawal of ₹{amount} ({(amount/customer.balance)*100:.1f}% of balance)',
            severity='high'
        )
        db.session.add(alert)
        db.session.commit()
        return True
    
    # Unusual transaction pattern (multiple transactions in short time)
    recent_transactions = Transaction.query.filter(
        Transaction.customer_id == customer_id,
        Transaction.created_at >= datetime.utcnow() - timedelta(hours=1)
    ).count()
    
    if recent_transactions > 5:
        alert = FraudAlert(
            customer_id=customer_id,
            alert_type='unusual_transaction',
            description=f'Multiple transactions ({recent_transactions}) in last hour',
            severity='medium'
        )
        db.session.add(alert)
        db.session.commit()
        return True
    
    return False

def calculate_emi(principal, annual_rate, tenure_months):
    """Calculate EMI using standard formula"""
    monthly_rate = annual_rate / (12 * 100)
    emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    return round(emi, 2)

def calculate_fd_maturity(principal, annual_rate, tenure_months):
    """Calculate FD maturity amount"""
    return round(principal * (1 + (annual_rate / 100)) ** (tenure_months / 12), 2)

# Authentication decorator
def login_required(role=None):
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            user = User.query.get(session['user_id'])
            if not user or not user.is_active:
                return jsonify({'error': 'Invalid user'}), 401
            
            if role and user.role != role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard/customer')
def customer_dashboard():
    return render_template('customer_dashboard.html')

@app.route('/dashboard/staff')
def staff_dashboard():
    return render_template('staff_dashboard.html')

@app.route('/dashboard/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin')
def admin_login_page():
    return render_template('admin_login.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact_page():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        if name and email and message:
            contact = ContactMessage(name=name, email=email, message=message)
            db.session.add(contact)
            db.session.commit()
            flash('Your message has been sent!', 'success')
            return redirect(url_for('contact_page'))
        else:
            flash('Please fill out all fields.', 'danger')
    return render_template('contact.html')

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
    
    # Create user
    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=password_hash,
        role=data.get('role', 'customer'),
        phone=data['phone']
    )
    
    db.session.add(user)
    db.session.commit()

    # If role is customer, auto-create a pending Customer profile and generate account number
    if user.role == 'customer':
        last_customer = Customer.query.order_by(Customer.id.desc()).first()
        next_id = (last_customer.id + 1) if last_customer else 1
        account_number = f"ACC{next_id:08d}"

        customer = Customer(
            user_id=user.id,
            account_number=account_number,
            first_name=data.get('first_name', user.username),
            last_name=data.get('last_name', ''),
            email=data['email'],
            phone=data['phone'],
            kyc_verified=False,
            account_status='pending'
        )

        # Optional KYC fields
        if data.get('pan_number'):
            customer.pan_number = data['pan_number']
        if data.get('aadhar_number'):
            customer.aadhar_number = data['aadhar_number']
        if data.get('address'):
            customer.address = data['address']
        if data.get('date_of_birth'):
            try:
                customer.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except Exception:
                pass

        db.session.add(customer)
        db.session.commit()

    return jsonify({'message': 'User registered successfully', 'user_id': user.id}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 400
        
        # Update last login and mark OTP as verified (skip 2FA)
        user.last_login = datetime.utcnow()
        user.otp_verified = True
        db.session.commit()
        
        # Create session
        session['user_id'] = user.id
        session['user_role'] = user.role
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'requires_2fa': False
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    
    user = User.query.get(data['user_id'])
    
    if user and user.otp_secret == data['otp']:
        user.otp_verified = True
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create session
        session['user_id'] = user.id
        session['user_role'] = user.role
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        })
    
    return jsonify({'error': 'Invalid OTP'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/profile', methods=['GET'])
@login_required()
def get_profile():
    user = User.query.get(session['user_id'])
    return jsonify(user.to_dict())

# Customer Management Routes
@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([customer.to_dict() for customer in customers])

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict())

@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    
    # For authenticated users, link to user account
    user_id = None
    if 'user_id' in session:
        user_id = session['user_id']
    
    # Generate account number
    last_customer = Customer.query.order_by(Customer.id.desc()).first()
    next_id = (last_customer.id + 1) if last_customer else 1
    account_number = f"ACC{next_id:08d}"
    
    customer = Customer(
        user_id=user_id,
        account_number=account_number,
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data['phone'],
        kyc_verified=data.get('kyc_verified', False),
        account_status='pending'
    )
    
    # Add KYC data if provided
    if 'pan_number' in data:
        customer.pan_number = data['pan_number']
    if 'aadhar_number' in data:
        customer.aadhar_number = data['aadhar_number']
    if 'address' in data:
        customer.address = data['address']
    if 'date_of_birth' in data:
        customer.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify(customer.to_dict()), 201

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    
    customer.first_name = data.get('first_name', customer.first_name)
    customer.last_name = data.get('last_name', customer.last_name)
    customer.email = data.get('email', customer.email)
    customer.phone = data.get('phone', customer.phone)
    
    db.session.commit()
    return jsonify(customer.to_dict())

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return '', 204

# Transaction Routes
@app.route('/api/customers/<int:customer_id>/deposit', methods=['POST'])
def deposit_money(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    amount = float(data['amount'])
    
    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400
    
    customer.balance += amount
    
    transaction = Transaction(
        customer_id=customer_id,
        transaction_type='deposit',
        amount=amount,
        balance_after=customer.balance,
        description=f"Cash deposit of ₹{amount}"
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Deposit successful',
        'new_balance': customer.balance,
        'transaction': transaction.to_dict()
    })

@app.route('/api/customers/<int:customer_id>/withdraw', methods=['POST'])
def withdraw_money(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    amount = float(data['amount'])
    
    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400
    
    if customer.balance < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Check for fraud conditions
    fraud_detected = check_fraud_conditions(customer_id, amount, 'withdraw')
    
    customer.balance -= amount
    
    transaction = Transaction(
        customer_id=customer_id,
        transaction_type='withdraw',
        amount=amount,
        balance_after=customer.balance,
        description=f"Cash withdrawal of ₹{amount}"
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    response_data = {
        'message': 'Withdrawal successful',
        'new_balance': customer.balance,
        'transaction': transaction.to_dict()
    }
    
    if fraud_detected:
        response_data['fraud_alert'] = 'Transaction flagged for review'
    
    return jsonify(response_data)

@app.route('/api/customers/<int:customer_id>/transfer', methods=['POST'])
def transfer_money(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    amount = float(data['amount'])
    to_customer_id = int(data['to_customer_id'])
    
    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400
    
    if customer.balance < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    to_customer = Customer.query.get_or_404(to_customer_id)
    
    # Update balances
    customer.balance -= amount
    to_customer.balance += amount
    
    # Create transactions
    from_transaction = Transaction(
        customer_id=customer_id,
        transaction_type='transfer',
        amount=amount,
        balance_after=customer.balance,
        description=f"Transfer to {to_customer.first_name} {to_customer.last_name}",
        related_customer_id=to_customer_id
    )
    
    to_transaction = Transaction(
        customer_id=to_customer_id,
        transaction_type='transfer',
        amount=amount,
        balance_after=to_customer.balance,
        description=f"Transfer from {customer.first_name} {customer.last_name}",
        related_customer_id=customer_id
    )
    
    db.session.add(from_transaction)
    db.session.add(to_transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Transfer successful',
        'from_balance': customer.balance,
        'to_balance': to_customer.balance,
        'from_transaction': from_transaction.to_dict(),
        'to_transaction': to_transaction.to_dict()
    })

@app.route('/api/customers/<int:customer_id>/transactions', methods=['GET'])
def get_transactions(customer_id):
    transactions = Transaction.query.filter_by(customer_id=customer_id).order_by(Transaction.created_at.desc()).limit(10).all()
    return jsonify([transaction.to_dict() for transaction in transactions])

@app.route('/api/customers/<int:customer_id>/balance', methods=['GET'])
def get_balance(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({'balance': customer.balance})

# Loan Management Routes
# @app.route('/api/loans', methods=['POST'])
# @login_required()
# def apply_loan():
#     data = request.get_json()
    
#     # Get customer from user
#     customer = Customer.query.filter_by(user_id=session['user_id']).first()
#     if not customer:
#         return jsonify({'error': 'Customer account not found'}), 404
    
    # Calculate EMI
    # emi = calculate_emi(data['amount'], data['interest_rate'], data['tenure_months'])
    
    # loan = Loan(
    #     customer_id=customer.id,
    #     loan_type=data['loan_type'],
    #     amount=data['amount'],
    #     interest_rate=data['interest_rate'],
    #     tenure_months=data['tenure_months'],
    #     emi_amount=emi,
    #     status='pending'
    # )
    
    # db.session.add(loan)
    # db.session.commit()
    
    # return jsonify(loan.to_dict()), 201

# @app.route('/api/loans', methods=['GET'])
# @login_required()
# def get_loans():
#     customer = Customer.query.filter_by(user_id=session['user_id']).first()
#     if not customer:
#         return jsonify({'error': 'Customer account not found'}), 404
    
#     loans = Loan.query.filter_by(customer_id=customer.id).all()
#     return jsonify([loan.to_dict() for loan in loans])

# @app.route('/api/loans/<int:loan_id>/approve', methods=['POST'])
# @login_required(role='staff')
# def approve_loan(loan_id):
#     loan = Loan.query.get_or_404(loan_id)
    
#     loan.status = 'approved'
#     loan.approved_at = datetime.utcnow()
#     loan.approved_by = session['user_id']
    
#     db.session.commit()
    
#     return jsonify({'message': 'Loan approved successfully', 'loan': loan.to_dict()})

# Deposit Management Routes
@app.route('/api/deposits', methods=['POST'])
@login_required()
def create_deposit():
    data = request.get_json()
    
    # Get customer from user
    customer = Customer.query.filter_by(user_id=session['user_id']).first()
    if not customer:
        return jsonify({'error': 'Customer account not found'}), 404
    
    # Check if customer has sufficient balance for FD
    if data['deposit_type'] == 'fixed' and customer.balance < data['amount']:
        return jsonify({'error': 'Insufficient balance for fixed deposit'}), 400
    
    # Calculate maturity amount
    maturity_amount = calculate_fd_maturity(data['amount'], data['interest_rate'], data['tenure_months'])
    
    # Calculate maturity date
    maturity_date = datetime.utcnow() + timedelta(days=data['tenure_months'] * 30)
    
    deposit = Deposit(
        customer_id=customer.id,
        deposit_type=data['deposit_type'],
        amount=data['amount'],
        interest_rate=data['interest_rate'],
        tenure_months=data['tenure_months'],
        maturity_amount=maturity_amount,
        maturity_date=maturity_date,
        status='active'
    )
    
    # Deduct amount from balance for fixed deposit
    if data['deposit_type'] == 'fixed':
        customer.balance -= data['amount']
        
        # Create transaction record
        transaction = Transaction(
            customer_id=customer.id,
            transaction_type='withdraw',
            amount=data['amount'],
            balance_after=customer.balance,
            description=f"Fixed Deposit of ₹{data['amount']}"
        )
        db.session.add(transaction)
    
    db.session.add(deposit)
    db.session.commit()
    
    return jsonify(deposit.to_dict()), 201

@app.route('/api/deposits', methods=['GET'])
@login_required()
def get_deposits():
    customer = Customer.query.filter_by(user_id=session['user_id']).first()
    if not customer:
        return jsonify({'error': 'Customer account not found'}), 404
    
    deposits = Deposit.query.filter_by(customer_id=customer.id).all()
    return jsonify([deposit.to_dict() for deposit in deposits])

# Fraud Detection Routes
@app.route('/api/fraud-alerts', methods=['GET'])
@login_required(role='admin')
def get_fraud_alerts():
    alerts = FraudAlert.query.filter_by(status='open').order_by(FraudAlert.created_at.desc()).all()
    return jsonify([alert.to_dict() for alert in alerts])

@app.route('/api/fraud-alerts/<int:alert_id>/resolve', methods=['POST'])
@login_required(role='admin')
def resolve_fraud_alert(alert_id):
    alert = FraudAlert.query.get_or_404(alert_id)
    
    alert.status = 'resolved'
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = session['user_id']
    
    db.session.commit()
    
    return jsonify({'message': 'Alert resolved successfully'})

# Admin Routes
@app.route('/api/admin/pending-accounts', methods=['GET'])
@login_required(role='admin')
def get_pending_accounts():
    """Get all pending account requests"""
    pending_customers = Customer.query.filter_by(account_status='pending').all()
    return jsonify([customer.to_dict() for customer in pending_customers])

@app.route('/api/admin/approve-account/<int:customer_id>', methods=['POST'])
@login_required(role='admin')
def approve_account(customer_id):
    """Approve a customer account"""
    customer = Customer.query.get_or_404(customer_id)
    customer.account_status = 'active'
    db.session.commit()
    return jsonify({'message': 'Account approved successfully'})

@app.route('/api/admin/reject-account/<int:customer_id>', methods=['POST'])
@login_required(role='admin')
def reject_account(customer_id):
    """Reject a customer account"""
    customer = Customer.query.get_or_404(customer_id)
    customer.account_status = 'rejected'
    db.session.commit()
    return jsonify({'message': 'Account rejected successfully'})

@app.route('/api/admin/all-accounts', methods=['GET'])
@login_required(role='admin')
def get_all_accounts():
    """Get all customer accounts with details"""
    customers = Customer.query.all()
    accounts_data = []
    
    for customer in customers:
        account_data = customer.to_dict()
        # Add user information
        user = User.query.get(customer.user_id)
        if user:
            account_data['username'] = user.username
            account_data['email'] = user.email
            account_data['phone'] = user.phone
            account_data['is_active'] = user.is_active
            account_data['last_login'] = user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
        
        # Add transaction count
        transaction_count = Transaction.query.filter_by(customer_id=customer.id).count()
        account_data['transaction_count'] = transaction_count
        
        accounts_data.append(account_data)
    
    return jsonify(accounts_data)

# Admin KYC Routes
@app.route('/api/admin/pending-kyc', methods=['GET'])
@login_required(role='admin')
def get_pending_kyc():
    """Get all customers with KYC pending"""
    pending_kyc = Customer.query.filter_by(kyc_verified=False).all()
    return jsonify([customer.to_dict() for customer in pending_kyc])

@app.route('/api/admin/approve-kyc/<int:customer_id>', methods=['POST'])
@login_required(role='admin')
def approve_kyc(customer_id):
    """Approve KYC for a customer"""
    customer = Customer.query.get_or_404(customer_id)
    customer.kyc_verified = True
    db.session.commit()
    return jsonify({'message': 'KYC approved successfully'})

@app.route('/api/admin/reject-kyc/<int:customer_id>', methods=['POST'])
@login_required(role='admin')
def reject_kyc(customer_id):
    """Reject KYC for a customer (keeps kyc_verified as False)"""
    customer = Customer.query.get_or_404(customer_id)
    customer.kyc_verified = False
    db.session.commit()
    return jsonify({'message': 'KYC rejected successfully'})

@app.route('/api/admin/backfill-customers', methods=['POST'])
@login_required(role='admin')
def backfill_customers():
    """Create Customer profiles for existing users (by username) who don't have one."""
    data = request.get_json() or {}
    usernames = data.get('usernames') or []

    if not isinstance(usernames, list) or not usernames:
        return jsonify({'error': 'Provide usernames as a non-empty list'}), 400

    results = []

    # Get current last id once; account_number will be sequential as we add
    last_customer = Customer.query.order_by(Customer.id.desc()).first()
    next_id = (last_customer.id + 1) if last_customer else 1

    for username in usernames:
        user = User.query.filter_by(username=username).first()
        if not user:
            results.append({'username': username, 'status': 'error', 'message': 'User not found'})
            continue

        if user.role != 'customer':
            results.append({'username': username, 'status': 'skipped', 'message': 'User is not a customer'})
            continue

        existing = Customer.query.filter_by(user_id=user.id).first()
        if existing:
            results.append({'username': username, 'status': 'skipped', 'message': 'Customer already exists', 'customer_id': existing.id})
            continue

        account_number = f"ACC{next_id:08d}"
        next_id += 1

        customer = Customer(
            user_id=user.id,
            account_number=account_number,
            first_name=user.username,
            last_name='',
            email=user.email,
            phone=user.phone,
            kyc_verified=False,
            account_status='pending'
        )

        db.session.add(customer)
        results.append({'username': username, 'status': 'created', 'account_number': account_number})

    db.session.commit()

    return jsonify({'results': results})

# Analytics Routes
@app.route('/api/analytics/dashboard', methods=['GET'])
@login_required(role='admin')
def get_analytics():
    total_customers = Customer.query.count()
    total_balance = db.session.query(db.func.sum(Customer.balance)).scalar() or 0
    total_loans = Loan.query.filter_by(status='approved').count()
    total_deposits = Deposit.query.filter_by(status='active').count()
    pending_loans = Loan.query.filter_by(status='pending').count()
    open_alerts = FraudAlert.query.filter_by(status='open').count()
    
    return jsonify({
        'total_customers': total_customers,
        'total_balance': total_balance,
        'total_loans': total_loans,
        'total_deposits': total_deposits,
        'pending_loans': pending_loans,
        'open_alerts': open_alerts
    })

def create_default_admin():
    """Create default admin account if it doesn't exist"""
    admin_email = 'admin@securebank.com'
    admin_user = User.query.filter_by(email=admin_email).first()
    
    if not admin_user:
        password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(
            username='admin',
            email=admin_email,
            password_hash=password_hash,
            role='admin',
            phone='9999999999'
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Default admin created - Email: {admin_email}, Password: admin123")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_admin()
    
    # For production deployment on Render
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)

