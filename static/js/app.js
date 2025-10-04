// Banking Automation System - JavaScript

// Global variables
let customers = [];
let currentSection = 'dashboard';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadCustomers();
    setupEventListeners();
    showSection('dashboard');
});

// Setup event listeners
function setupEventListeners() {
    // Customer form
    document.getElementById('customerForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveCustomer();
    });

    // Transaction forms
    document.getElementById('depositForm').addEventListener('submit', function(e) {
        e.preventDefault();
        performTransaction('deposit');
    });

    document.getElementById('withdrawForm').addEventListener('submit', function(e) {
        e.preventDefault();
        performTransaction('withdraw');
    });

    document.getElementById('transferForm').addEventListener('submit', function(e) {
        e.preventDefault();
        performTransaction('transfer');
    });

    document.getElementById('balanceForm').addEventListener('submit', function(e) {
        e.preventDefault();
        checkBalance();
    });

    document.getElementById('statementForm').addEventListener('submit', function(e) {
        e.preventDefault();
        generateStatement();
    });

    // Customer dropdowns change events
    document.getElementById('depositCustomer').addEventListener('change', function() {
        updateCustomerInfo('deposit');
    });

    document.getElementById('withdrawCustomer').addEventListener('change', function() {
        updateCustomerInfo('withdraw');
    });

    document.getElementById('transferFrom').addEventListener('change', function() {
        updateCustomerInfo('transfer');
    });

    document.getElementById('balanceCustomer').addEventListener('change', function() {
        updateCustomerInfo('balance');
    });

    document.getElementById('statementCustomer').addEventListener('change', function() {
        updateCustomerInfo('statement');
    });
}

// Show/hide sections
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });

    // Show selected section
    document.getElementById(sectionName).style.display = 'block';
    currentSection = sectionName;

    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    if (sectionName === 'dashboard') {
        updateDashboard();
    } else if (sectionName === 'customers') {
        loadCustomers();
    } else if (sectionName === 'transactions' || sectionName === 'reports') {
        updateCustomerDropdowns();
    }
}

// Load customers from API
async function loadCustomers() {
    try {
        const response = await fetch('/api/customers');
        customers = await response.json();
        updateCustomersTable();
        updateCustomerDropdowns();
        updateDashboard();
    } catch (error) {
        showToast('error', 'Failed to load customers: ' + error.message);
    }
}

// Update customers table
function updateCustomersTable() {
    const tbody = document.getElementById('customersTable');
    tbody.innerHTML = '';

    customers.forEach(customer => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${customer.account_number}</strong></td>
            <td>${customer.first_name} ${customer.last_name}</td>
            <td>${customer.email}</td>
            <td>${customer.phone}</td>
            <td><span class="currency">₹${customer.balance.toFixed(2)}</span></td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="editCustomer(${customer.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-info" onclick="viewCustomerDetails(${customer.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteCustomer(${customer.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Update customer dropdowns
function updateCustomerDropdowns() {
    const dropdowns = [
        'depositCustomer', 'withdrawCustomer', 'transferFrom', 'transferTo',
        'balanceCustomer', 'statementCustomer'
    ];

    dropdowns.forEach(dropdownId => {
        const dropdown = document.getElementById(dropdownId);
        const currentValue = dropdown.value;
        
        dropdown.innerHTML = '<option value="">Choose customer...</option>';
        
        customers.forEach(customer => {
            const option = document.createElement('option');
            option.value = customer.id;
            option.textContent = `${customer.account_number} - ${customer.first_name} ${customer.last_name}`;
            dropdown.appendChild(option);
        });

        // Restore previous selection if valid
        if (currentValue && customers.find(c => c.id == currentValue)) {
            dropdown.value = currentValue;
        }
    });
}

// Save customer (create or update)
async function saveCustomer() {
    const customerId = document.getElementById('customerId').value;
    const customerData = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value
    };

    try {
        let response;
        if (customerId) {
            // Update existing customer
            response = await fetch(`/api/customers/${customerId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(customerData)
            });
        } else {
            // Create new customer
            response = await fetch('/api/customers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(customerData)
            });
        }

        if (response.ok) {
            const customer = await response.json();
            showToast('success', customerId ? 'Customer updated successfully!' : 'Customer created successfully!');
            bootstrap.Modal.getInstance(document.getElementById('customerModal')).hide();
            resetCustomerForm();
            loadCustomers();
        } else {
            const error = await response.json();
            showToast('error', error.error || 'Failed to save customer');
        }
    } catch (error) {
        showToast('error', 'Failed to save customer: ' + error.message);
    }
}

// Edit customer
function editCustomer(customerId) {
    const customer = customers.find(c => c.id === customerId);
    if (!customer) return;

    document.getElementById('customerId').value = customer.id;
    document.getElementById('firstName').value = customer.first_name;
    document.getElementById('lastName').value = customer.last_name;
    document.getElementById('email').value = customer.email;
    document.getElementById('phone').value = customer.phone;
    document.getElementById('customerModalTitle').textContent = 'Edit Customer';

    const modal = new bootstrap.Modal(document.getElementById('customerModal'));
    modal.show();
}

// View customer details
function viewCustomerDetails(customerId) {
    const customer = customers.find(c => c.id === customerId);
    if (!customer) return;

    alert(`Customer Details:\n\n` +
          `Account Number: ${customer.account_number}\n` +
          `Name: ${customer.first_name} ${customer.last_name}\n` +
          `Email: ${customer.email}\n` +
          `Phone: ${customer.phone}\n` +
          `Balance: ₹${customer.balance.toFixed(2)}\n` +
          `Created: ${new Date(customer.created_at).toLocaleDateString()}`);
}

// Delete customer
async function deleteCustomer(customerId) {
    if (!confirm('Are you sure you want to delete this customer?')) {
        return;
    }

    try {
        const response = await fetch(`/api/customers/${customerId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('success', 'Customer deleted successfully!');
            loadCustomers();
        } else {
            showToast('error', 'Failed to delete customer');
        }
    } catch (error) {
        showToast('error', 'Failed to delete customer: ' + error.message);
    }
}

// Reset customer form
function resetCustomerForm() {
    document.getElementById('customerForm').reset();
    document.getElementById('customerId').value = '';
    document.getElementById('customerModalTitle').textContent = 'Add New Customer';
}

// Perform transaction (deposit, withdraw, transfer)
async function performTransaction(type) {
    const customerId = document.getElementById(`${type}Customer`).value;
    const amount = parseFloat(document.getElementById(`${type}Amount`).value);

    if (!customerId || !amount || amount <= 0) {
        showToast('error', 'Please enter valid customer and amount');
        return;
    }

    try {
        let response;
        let requestData = { amount: amount };

        if (type === 'transfer') {
            const toCustomerId = document.getElementById('transferTo').value;
            if (!toCustomerId || customerId === toCustomerId) {
                showToast('error', 'Please select different customers for transfer');
                return;
            }
            requestData.to_customer_id = toCustomerId;
        }

        response = await fetch(`/api/customers/${customerId}/${type}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();

        if (response.ok) {
            showToast('success', result.message);
            document.getElementById(`${type}Form`).reset();
            loadCustomers();
            updateDashboard();
        } else {
            showToast('error', result.error || 'Transaction failed');
        }
    } catch (error) {
        showToast('error', 'Transaction failed: ' + error.message);
    }
}

// Check balance
async function checkBalance() {
    const customerId = document.getElementById('balanceCustomer').value;
    
    if (!customerId) {
        showToast('error', 'Please select a customer');
        return;
    }

    try {
        const response = await fetch(`/api/customers/${customerId}/balance`);
        const result = await response.json();

        if (response.ok) {
            document.getElementById('balanceAmount').textContent = `₹${result.balance.toFixed(2)}`;
            document.getElementById('balanceResult').style.display = 'block';
        } else {
            showToast('error', 'Failed to get balance');
        }
    } catch (error) {
        showToast('error', 'Failed to get balance: ' + error.message);
    }
}

// Generate mini statement
async function generateStatement() {
    const customerId = document.getElementById('statementCustomer').value;
    
    if (!customerId) {
        showToast('error', 'Please select a customer');
        return;
    }

    try {
        const response = await fetch(`/api/customers/${customerId}/transactions`);
        const transactions = await response.json();

        if (response.ok) {
            const tbody = document.getElementById('statementTable');
            tbody.innerHTML = '';

            if (transactions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No transactions found</td></tr>';
            } else {
                transactions.forEach(transaction => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${new Date(transaction.created_at).toLocaleDateString()}</td>
                        <td><span class="transaction-${transaction.transaction_type}">${transaction.transaction_type.toUpperCase()}</span></td>
                        <td class="currency">₹${transaction.amount.toFixed(2)}</td>
                        <td class="currency">₹${transaction.balance_after.toFixed(2)}</td>
                        <td>${transaction.description || '-'}</td>
                    `;
                    tbody.appendChild(row);
                });
            }

            document.getElementById('statementResult').style.display = 'block';
        } else {
            showToast('error', 'Failed to generate statement');
        }
    } catch (error) {
        showToast('error', 'Failed to generate statement: ' + error.message);
    }
}

// Update customer info display
function updateCustomerInfo(type) {
    const customerId = document.getElementById(`${type}Customer`).value;
    const customer = customers.find(c => c.id == customerId);
    
    if (customer) {
        // You can add customer info display here if needed
        console.log(`Selected customer for ${type}:`, customer);
    }
}

// Update dashboard statistics
function updateDashboard() {
    const totalCustomers = customers.length;
    const totalBalance = customers.reduce((sum, customer) => sum + customer.balance, 0);
    
    document.getElementById('totalCustomers').textContent = totalCustomers;
    document.getElementById('totalBalance').textContent = `₹${totalBalance.toFixed(2)}`;
    document.getElementById('todayTransactions').textContent = '0'; // This would need backend support
    document.getElementById('activeAccounts').textContent = totalCustomers;
}

// Show toast notification
function showToast(type, message) {
    const toastElement = document.getElementById(`${type}Toast`);
    const messageElement = document.getElementById(`${type}Message`);
    
    messageElement.textContent = message;
    
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(amount);
}

// Utility function to format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}
