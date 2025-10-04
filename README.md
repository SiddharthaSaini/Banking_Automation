# Advanced Banking Automation System

A comprehensive, enterprise-grade banking automation system built with Flask, SQLite, and Bootstrap 5. Features role-based authentication, fraud detection, loan management, and advanced analytics.

## 🚀 Key Features

### 🔐 User Authentication & Security
- ✅ **Role-based login system** (Customer, Bank Staff, Admin)
- ✅ **Secure password hashing** with bcrypt
- ✅ **2FA/OTP simulation** for enhanced security
- ✅ **Session management** with secure cookies
- ✅ **Multi-factor authentication** workflow

### 👥 Customer Services (Customer Dashboard)
- ✅ **Account creation & KYC verification**
- ✅ **Real-time balance inquiry**
- ✅ **Deposit/Withdraw operations**
- ✅ **Money transfer** (same bank or inter-bank simulation)
- ✅ **Transaction history & mini statement**
- ✅ **Personal dashboard** with account overview
- ✅ **KYC status tracking**

### 🏦 Staff/Bank Officer Dashboard
- ✅ **Approve new customer accounts**
- ✅ **Loan management system**
  - Apply for loans
  - Approve/reject loan applications
  - EMI calculator with interest computation
  - Loan repayment tracking
- ✅ **Fixed deposits management**
- ✅ **Recurring deposits management**
- ✅ **Customer account oversight**

### 🔧 Admin Dashboard
- ✅ **Manage staff & customer accounts**
- ✅ **Fraud detection alerts**
  - Large withdrawal detection
  - Unusual transaction patterns
  - Multiple failed login attempts
- ✅ **Analytics dashboard**
  - New accounts trends
  - Transaction volume analysis
  - Loan portfolio overview
  - Deposit statistics
- ✅ **System administration tools**

### 💰 Banking Operations
- ✅ **Deposit money** with real-time balance update
- ✅ **Withdraw money** with balance validation
- ✅ **Transfer money** between accounts
- ✅ **Check account balance** instantly
- ✅ **Transaction history** with detailed records
- ✅ **Mini statement** generation

### 🏠 Dynamic Homepage
- ✅ **Attractive landing page** with service details
- ✅ **Realistic banking information**
- ✅ **Service highlights** and testimonials
- ✅ **Responsive design** for all devices
- ✅ **Professional branding** and UI/UX

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML/CSS (Bootstrap 5) + JavaScript (Fetch/AJAX)
- **UI**: Modern, mobile-friendly design with Indian currency (₹) support

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or download the project**
   ```bash
   cd Banking_Automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - The application will automatically create the database on first run

## Usage Guide

### 1. Customer Management
- Click on "Customers" in the navigation menu
- Use "Add New Customer" button to create new accounts
- Edit customer details using the edit button
- View customer information using the eye icon
- Delete customers using the trash icon

### 2. Banking Transactions
- Navigate to "Transactions" section
- **Deposit**: Select customer and enter amount
- **Withdraw**: Select customer and enter amount (validates sufficient balance)
- **Transfer**: Select from/to customers and enter amount
- **Check Balance**: Select customer to view current balance

### 3. Transaction Reports
- Go to "Reports" section
- Generate mini statements for any customer
- View recent transaction history (last 10 transactions)

## Database Schema

### Customers Table
- `id` (Primary Key)
- `account_number` (Unique, Auto-generated)
- `first_name`
- `last_name`
- `email` (Unique)
- `phone`
- `balance` (Default: 0.0)
- `created_at` (Timestamp)

### Transactions Table
- `id` (Primary Key)
- `customer_id` (Foreign Key)
- `transaction_type` (deposit/withdraw/transfer)
- `amount`
- `balance_after`
- `description`
- `related_customer_id` (For transfers)
- `created_at` (Timestamp)

## API Endpoints

### Customer Management
- `GET /api/customers` - Get all customers
- `GET /api/customers/<id>` - Get specific customer
- `POST /api/customers` - Create new customer
- `PUT /api/customers/<id>` - Update customer
- `DELETE /api/customers/<id>` - Delete customer

### Transactions
- `POST /api/customers/<id>/deposit` - Deposit money
- `POST /api/customers/<id>/withdraw` - Withdraw money
- `POST /api/customers/<id>/transfer` - Transfer money
- `GET /api/customers/<id>/balance` - Get balance
- `GET /api/customers/<id>/transactions` - Get transaction history

## Features Highlights

### Modern UI/UX
- Responsive Bootstrap 5 design
- Mobile-friendly interface
- Indian currency (₹) support throughout
- Toast notifications for user feedback
- Modal dialogs for forms
- Smooth animations and transitions

### Security Features
- Input validation on both client and server side
- Balance validation for withdrawals and transfers
- SQL injection protection via SQLAlchemy ORM
- Error handling and user feedback

### User Experience
- Real-time dashboard with statistics
- Intuitive navigation
- Form validation with visual feedback
- Loading states and error handling
- Responsive design for all screen sizes

## File Structure

```
Banking_Automation/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Custom styles
    └── js/
        └── app.js        # JavaScript functionality
```

## Development Notes

- The application uses SQLite database which is created automatically
- Account numbers are auto-generated in format: ACC00000001, ACC00000002, etc.
- All monetary values are stored as floats with 2 decimal precision
- The frontend uses Fetch API for AJAX requests
- Bootstrap 5 provides the responsive UI framework

## Future Enhancements

Potential features for future versions:
- User authentication and role-based access
- Advanced reporting and analytics
- Email/SMS notifications
- Multi-currency support
- Interest calculation
- Loan management
- Advanced security features

## Support

For issues or questions, please check the code comments or create an issue in the project repository.

---

**Note**: This is a basic version for demonstration purposes. For production use, additional security measures, authentication, and data validation would be required.
