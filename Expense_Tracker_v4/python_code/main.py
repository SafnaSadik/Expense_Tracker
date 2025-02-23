!pip install flask flask-sqlalchemy flask-session flask-pymongo flask-pyngrok pymongo dnspython reportlab flask-ngrok

!pip install "pymongo[srv]" dnspython

import os

os.makedirs("templates", exist_ok=True)

# Save base.html
base_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Expense Tracker{% endblock %}</title>

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">

    <!-- Custom Styles -->
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">

    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">Expense Tracker</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if session.get('logged_in') %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link btn btn-danger text-white px-3 py-1" href="{{ url_for('logout') }}">Logout</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('login') }}">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('register') }}">Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Page Content -->
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>"""
with open("templates/base.html", "w") as file:
    file.write(base_html)

# Save register.html
register_html = """    {% extends "base.html" %}
    {% block title %}Register - Expense Tracker{% endblock %}

    {% block content %}
    <div class="d-flex justify-content-center align-items-center vh-100">
        <div class="card shadow-lg border-0 rounded-lg p-4" style="max-width: 400px; width: 100%;">
            <div class="card-body">
                <h3 class="text-center text-primary mb-3">Create Account</h3>

                <!-- Flash Messages -->
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}

                <!-- Register Form -->
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" id="username" name="username" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" id="email" name="email" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" id="password" name="password" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="confirm_password" class="form-label">Confirm Password</label>
                        <input type="password" id="confirm_password" name="confirm_password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Register</button>
                    <p class="text-center mt-3">
                        Already have an account? <a href="{{ url_for('login') }}" class="text-decoration-none">Login here</a>
                    </p>
                </form>
            </div>
        </div>
    </div>
    {% endblock %}"""

with open("templates/register.html", "w") as file:
    file.write(register_html)

# Save login.html
login_html = """{% extends "base.html" %}
{% block title %}Login - Expense Tracker{% endblock %}

{% block content %}
<div class="d-flex justify-content-center align-items-center vh-100">
    <div class="card shadow-lg border-0 rounded-lg p-4" style="max-width: 400px; width: 100%;">
        <div class="card-body">
            <h3 class="text-center text-primary mb-3">Welcome Back</h3>

            <!-- Flash Messages -->
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <!-- Login Form -->
            <form method="POST">
                <div class="mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input type="text" id="username" name="username" class="form-control" required>
                </div>

                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" id="password" name="password" class="form-control" required>
                </div>

                <button type="submit" class="btn btn-primary w-100">Login</button>

                <p class="text-center mt-3">
                    Don't have an account? <a href="{{ url_for('register') }}" class="text-decoration-none">Register here</a>
                </p>
            </form>
        </div>
    </div>
</div>
{% endblock %}"""

with open("templates/login.html", "w") as file:
    file.write(login_html)

# Save dashboard.html
dashboard_html = """{% extends "base.html" %}
{% block title %}Dashboard - Expense Tracker{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/flatpickr/4.6.13/flatpickr.min.css">
{% endblock %}

{% block content %}
<div class="container mt-4">
    <header class="d-flex justify-content-between align-items-center p-4 bg-primary text-white rounded shadow-lg border-0">
        <h1 class="h3">Expense Tracker</h1>
        <div class="user-info">
            <span>Welcome, {{ session.username }}!</span>
            <a href="{{ url_for('logout') }}" class="btn btn-light ms-3">Logout</a>
        </div>
    </header>

<!-- Summary Cards Row -->
<div class="row mb-4">
    <div class="col-md-4">
        <div class="card shadow-lg border-0 rounded-lg mt-4 p-4">
            <div class="card-body text-center">
                <h5 class="card-title text-muted mb-3">Total Expenses</h5>
                <p class="fs-4 text-danger mb-0">₹{{ "%.2f"|format(total_expenses) }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card shadow-lg border-0 rounded-lg mt-4 p-4">
            <div class="card-body text-center">
                <h5 class="card-title text-muted mb-3">Monthly Budget</h5>
                <p class="fs-4 text-primary mb-0">₹{{ "%.2f"|format(monthly_budget) }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card shadow-lg border-0 rounded-lg mt-4 p-4">
            <div class="card-body text-center">
                <h5 class="card-title text-muted mb-3">Remaining Budget</h5>
                <p class="fs-4 mb-0 {% if remaining_budget < 0 %}text-danger{% else %}text-success{% endif %}">
                    ₹{{ "%.2f"|format(remaining_budget) }}
                </p>
            </div>
        </div>
    </div>
</div>

<!-- Budget Management Section -->
    <div class="card shadow-lg border-0 rounded-lg mt-4 p-4">
        <div class="card-header bg-primary text-white rounded-top px-4 py-3 m-0">
            <h3 class="text-start mb-0">Budget Management</h3>
        </div>
        <div class="card-body p-4">
            <form id="budgetForm" class="needs-validation" novalidate>
                <div class="row align-items-end">
                    <div class="col-md-8">
                        <div class="form-floating">
                            <input type="number"
                                   name="amount"
                                   id="budgetAmount"
                                   class="form-control"
                                   step="0.01"
                                   min="0"
                                   placeholder="Enter amount"
                                   required>
                            <label for="budgetAmount">Monthly Budget (₹)*</label>
                            <div class="invalid-feedback">
                                Please enter a valid budget amount
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary btn-lg">Set Budget</button>
                        </div>
                    </div>
                </div>
            </form>
        </div>
    </div>

<!-- Budget Overview Section -->
    <div class="card shadow-lg border-0 rounded-lg mt-4 p-4">
        <div class="card-header bg-primary text-white rounded-top px-4 py-3 m-0">
            <h3 class="text-start mb-0">Budget Overview</h3>
        </div>
        <div class="card-body p-4">
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-light">
                        <tr>
                            <th>Monthly Budget</th>
                            <th>Date Added</th>
                            <th class="text-start">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="budgetTableBody">
                        <!-- Budget data will be populated here -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

<!-- Update Budget Modal -->
<div class="modal fade budget-modal" id="updateBudgetModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">
                    <i class="fas fa-wallet me-2"></i>Update Monthly Budget
                </h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body p-4">
                <input type="hidden" id="updateBudgetId">
                <div class="mb-4">
                    <label class="form-label fw-semibold">Budget Amount (₹)</label>
                    <div class="input-group">
                        <span class="input-group-text">₹</span>
                        <input type="number" id="updateBudgetAmount" class="form-control" step="0.01" min="0"
                            placeholder="Enter budget amount" required>
                        <span class="input-group-text">.00</span>
                    </div>
                    <div class="form-text text-muted">Enter your monthly budget limit</div>
                </div>
            </div>
            <div class="modal-footer bg-light">
                <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                    <i class="fas fa-times me-2"></i>Cancel
                </button>
                <button type="button" class="btn btn-primary" onclick="handleBudgetUpdate()">
                    <i class="fas fa-check me-2"></i>Update Budget
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Alert Container -->
<div id="alertContainer" class="position-fixed top-0 end-0 p-3" style="z-index: 1050">
    <!-- Alerts will be dynamically inserted here -->
</div>

        <!-- Add Expense Form -->
    <div class="card shadow-lg border-0 rounded-lg mt-4 p-4">
      <div class="card-header bg-primary text-white rounded-top px-4 py-3 m-0">
        <h3 class="text-start mb-0">Add New Expense</h3>
      </div>
        <div class="card-body p-4">
            <form id="expense-form" onsubmit="addExpense(event)">
                <div class="row">
                    <!-- Expense Name -->
                    <div class="col-md-6 mb-3">
                        <div class="form-floating">
                            <input type="text" class="form-control" id="expense-name" name="name" placeholder="Enter expense name" required>
                            <label for="expense-name">Expense Name*</label>
                        </div>
                    </div>

                    <!-- Amount -->
                    <div class="col-md-6 mb-3">
                        <div class="form-floating">
                            <input type="number" class="form-control" id="amount" name="amount" step="0.01" min="0.01" placeholder="Enter amount" required>
                            <label for="amount">Amount*</label>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <!-- Category -->
                    <div class="col-md-6 mb-3">
                        <div class="form-floating">
                            <select class="form-select" id="category" name="category" required>
                                <option value="" disabled selected>Select a category</option>
                                {% for category in categories %}
                                    <option value="{{ category }}">{{ category }}</option>
                                {% endfor %}
                            </select>
                            <label for="category">Category*</label>
                        </div>
                    </div>

                    <!-- Date -->
                    <div class="col-md-6 mb-3">
                        <div class="form-floating">
                            <input type="date" class="form-control" id="date" name="date" required>
                            <label for="date">Date*</label>
                        </div>
                    </div>
                </div>

                <!-- Description -->
                <div class="mb-3">
                    <div class="form-floating">
                        <textarea class="form-control" id="description" name="description" style="height: 100px" placeholder="Enter description"></textarea>
                        <label for="description">Description</label>
                    </div>
                </div>

                <!-- Recurring Expense -->
                <div class="form-check mb-3">
                    <input type="checkbox" class="form-check-input" id="recurring" name="recurring">
                    <label class="form-check-label" for="recurring">
                        Recurring Expense
                    </label>
                </div>

                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary btn-lg">Add Expense</button>
                </div>
            </form>
        </div>
    </div>

        <!-- Expense Chart -->
        <div class="card shadow-lg border-0 rounded-lg mt-4 p-4">
            <h2>Expense Distribution</h2>
            <canvas id="expenseChart"></canvas>
        </div>

<!-- Transaction History Section -->
    <div class="card shadow-lg border-0 rounded-lg mt-4 p-4">
        <div class="card-header bg-primary text-white rounded-top px-4 py-3 m-0">
            <h3 class="text-start mb-0">Transaction History</h3>
        </div>
        <div class="card-body p-4">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-primary">
                        <tr>
                            <th>Date</th>
                            <th>Name</th>
                            <th>Category</th>
                            <th>Amount</th>
                            <th>Description</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for expense in expenses %}
                        <tr data-expense-id="{{ expense._id }}">
                            <td>{{ expense.date.strftime('%Y-%m-%d') }}</td>
                            <td>{{ expense.name }}</td>
                            <td>{{ expense.category }}</td>
                            <td>₹{{ "%.2f"|format(expense.amount) }}</td>
                            <td>{{ expense.description }}</td>
                            <td>
                                <button class="btn btn-warning btn-sm me-2">
                                    <i class="bi bi-pencil"></i> Edit
                                </button>
                                <button class="btn btn-danger btn-sm" onclick="deleteExpense('{{ expense._id }}')">
                                    <i class="bi bi-trash"></i> Delete
                                </button>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

<!-- Edit Expense Modal -->
<div class="modal fade expense-modal" id="editExpenseModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">
                    <i class="fas fa-edit me-2"></i>Edit Expense
                </h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body p-4">
                <form id="edit-expense-form" class="needs-validation" novalidate>
                    <input type="hidden" id="edit-expense-id">
                    <div class="mb-4">
                        <label for="edit-expense-name" class="form-label fw-semibold">Expense Name*</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="fas fa-tag"></i></span>
                            <input type="text" id="edit-expense-name" name="name" class="form-control" required>
                        </div>
                        <div class="invalid-feedback">Please enter an expense name.</div>
                    </div>
                    <div class="mb-4">
                        <label for="edit-amount" class="form-label fw-semibold">Amount*</label>
                        <div class="input-group">
                            <span class="input-group-text">₹</span>
                            <input type="number" id="edit-amount" name="amount" class="form-control" step="0.01" min="0.01" required>
                        </div>
                        <div class="invalid-feedback">Please enter a valid amount.</div>
                    </div>
                    <div class="mb-4">
                        <label for="edit-category" class="form-label fw-semibold">Category*</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="fas fa-folder"></i></span>
                            <select id="edit-category" name="category" class="form-select" required>
                                {% for category in categories %}
                                    <option value="{{ category }}">{{ category }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                    <div class="mb-4">
                        <label for="edit-date" class="form-label fw-semibold">Date*</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="fas fa-calendar"></i></span>
                            <input type="date" id="edit-date" name="date" class="form-control" required>
                        </div>
                    </div>
                    <div class="mb-4">
                        <label for="edit-description" class="form-label fw-semibold">Description</label>
                        <textarea id="edit-description" name="description" class="form-control" rows="3"
                            placeholder="Add any additional details here..."></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer bg-light">
                <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                    <i class="fas fa-times me-2"></i>Close
                </button>
                <button type="button" class="btn btn-primary" onclick="updateExpense(event)">
                    <i class="fas fa-save me-2"></i>Save Changes
                </button>
            </div>
        </div>
    </div>
</div>

        <!-- Export Options -->
        <div class="text-center mt-4">
            <button onclick="exportData('csv')" class="btn btn-primary">Export CSV</button>
            <button onclick="exportData('pdf')" class="btn btn-primary">Export PDF</button>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="https://cdnjs.cloudflare.com/ajax/libs/flatpickr/4.6.13/flatpickr.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    // Initialize date pickers
    flatpickr('input[type="date"]', {
        dateFormat: "Y-m-d"
    });

    // Toggle recurring options
    document.getElementById('recurring').addEventListener('change', function() {
        document.getElementById('recurringOptions').style.display =
            this.checked ? 'block' : 'none';
    });

const ctx = document.getElementById('expenseChart').getContext('2d');
new Chart(ctx, {
    type: 'pie',
    data: {
        labels: {{ categories|tojson }},
        datasets: [{
            data: {{ category_totals|tojson }},
            backgroundColor: {{ category_colors|tojson }},
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    // Show all labels even if value is 0
                    filter: function(legendItem, data) {
                        return true;
                    }
                }
            }
        }
    }
});
</script>

<script>

// Form submission handlers
document.getElementById('expenseForm')?.addEventListener('submit', addExpense);
document.getElementById('budgetForm')?.addEventListener('submit', handleBudgetSubmit);
document.getElementById('filterForm')?.addEventListener('submit', handleFilterSubmit);

// Export functions
function exportData(format) {
    window.location.href = `/export_data?format=${format}`;
}

// ============ EXPENSE OPERATIONS ============
async function addExpense(event) {
    event.preventDefault();

    const formData = {
        name: document.getElementById('expense-name').value,
        amount: document.getElementById('amount').value,
        category: document.getElementById('category').value,
        date: document.getElementById('date').value,
        description: document.getElementById('description')?.value || '',
        recurring: document.getElementById('recurring')?.checked || false
    };

    if (!formData.name || !formData.amount || !formData.category || !formData.date) {
        showAlert('Please fill in all required fields', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/expenses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        if (data.error) {
            showAlert(data.error, 'danger');
        } else {
            showAlert('Expense added successfully!', 'success');
            window.location.reload();
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error adding expense. Please try again.', 'danger');
    }
}

// Add event listeners to the Edit buttons
async function initializeExpenseHandlers() {
    // Add click handlers to all Edit buttons in the table
    document.querySelectorAll('.btn-warning').forEach(button => {
        button.onclick = function() {
            // Get the expense ID from the row
            const row = this.closest('tr');
            const expenseId = row.dataset.expenseId; // Make sure to add data-expense-id to your tr elements
            editExpense(expenseId);
        };
    });
}

async function editExpense(id) {
    try {
        const response = await fetch(`/api/expenses/${id}`);
        if (!response.ok) {
            throw new Error('Failed to fetch expense data');
        }
        const expense = await response.json();

        // Populate the edit form
        document.getElementById('edit-expense-id').value = expense._id;
        document.getElementById('edit-expense-name').value = expense.name;
        document.getElementById('edit-amount').value = expense.amount;
        document.getElementById('edit-category').value = expense.category;
        document.getElementById('edit-date').value = expense.date.split('T')[0];
        document.getElementById('edit-description').value = expense.description || '';

        // Create and show modal
        const editModal = new bootstrap.Modal(document.getElementById('editExpenseModal'));
        editModal.show();
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error loading expense details', 'danger');
    }
}

async function updateExpense(event) {
    event.preventDefault(); // Prevent default form submission

    // Validate form
    const form = document.getElementById('edit-expense-form');
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    const formData = {
        id: document.getElementById('edit-expense-id').value,
        name: document.getElementById('edit-expense-name').value,
        amount: parseFloat(document.getElementById('edit-amount').value),
        category: document.getElementById('edit-category').value,
        date: document.getElementById('edit-date').value,
        description: document.getElementById('edit-description').value
    };

    try {
        const response = await fetch('/api/expenses', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                // Add any authentication headers if needed
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Failed to update expense');
        }

        // Hide modal
        const editModal = bootstrap.Modal.getInstance(document.getElementById('editExpenseModal'));
        editModal.hide();

        showAlert('Expense updated successfully', 'success');
        window.location.reload();
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error updating expense', 'danger');
    }
}

// Modified delete function with better error handling
async function deleteExpense(id) {
    if (!confirm('Are you sure you want to delete this expense?')) return;

    try {
        const response = await fetch('/api/expenses', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                // Add any authentication headers if needed
            },
            body: JSON.stringify({ id })
        });

        if (!response.ok) {
            throw new Error('Failed to delete expense');
        }

        showAlert('Expense deleted successfully', 'success');
        window.location.reload();
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error deleting expense', 'danger');
    }
}

// Initialize handlers when the document is ready
document.addEventListener('DOMContentLoaded', initializeExpenseHandlers);

// ============ BUDGET OPERATIONS ============

document.addEventListener('DOMContentLoaded', initializeBudget);

// Initialize the budget when page loads
function initializeBudget() {
    fetchAndUpdateBudget();
}

// Show alert messages
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) {
        console.error('Alert container not found');
        return;
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    alertContainer.appendChild(alertDiv);

    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 150);
    }, 3000);
}

// Centralized function to fetch and update budget displays
async function fetchAndUpdateBudget() {
    try {
        const response = await fetch('/api/budget');
        const data = await response.json();
        console.log('Fetched Budget:', data);

        if (data.error) {
            console.error('Error fetching budget:', data.error);
            return;
        }

        const monthlyBudget = data.find(b => b.category === 'monthly');
        updateBudgetDisplays(monthlyBudget);
    } catch (error) {
        console.error('Error fetching budget:', error);
    }
}

// Update both the table and summary cards
function updateBudgetDisplays(monthlyBudget) {
    // Get total expenses from the UI
    const totalExpensesElement = document.querySelector('.card:nth-child(1) .fs-4');
    const totalExpensesStr = totalExpensesElement?.textContent || '₹0.00';
    const totalExpenses = parseFloat(totalExpensesStr.replace('₹', '')) || 0;

    // Update both displays
    displayBudgetInTable(monthlyBudget);
    updateSummaryCards(monthlyBudget, totalExpenses);
}

async function handleBudgetSubmit(e) {
    e.preventDefault();
    console.log('Form submitted');

    const amount = parseFloat(document.getElementById('budgetAmount').value);
    console.log('Amount:', amount);

    if (!amount || isNaN(amount)) {
        showAlert('Please enter a valid amount', 'warning');
        return;
    }

    const formData = {
        amount: amount,
        category: 'monthly'
    };

    try {
        const response = await fetch('/api/budget', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        console.log('API response:', data);

        if (data.error) {
            showAlert('Error setting budget', 'danger');
            return;
        }

        document.getElementById('budgetAmount').value = '';
        showAlert('Budget set successfully');
        window.location.reload();
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error setting budget', 'danger');
    }
}

async function handleBudgetUpdate() {
    const budgetId = document.getElementById('updateBudgetId').value;
    const amount = parseFloat(document.getElementById('updateBudgetAmount').value);

    if (!amount || isNaN(amount)) {
        showAlert('Please enter a valid amount', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/budget', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: budgetId,
                category: 'monthly',
                amount
            })
        });

        const data = await response.json();
        if (data.error) {
            showAlert(data.error || 'Error updating budget', 'danger');
            return;
        }

        const modalElement = document.getElementById('updateBudgetModal');
        const modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();

        showAlert('Budget updated successfully');
        window.location.reload();
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error updating budget', 'danger');
    }
}

async function deleteBudget(budgetId) {
    if (!confirm('Are you sure you want to delete this budget?')) return;

    try {
        const response = await fetch('/api/budget', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: budgetId })
        });

        const data = await response.json();
        if (data.error) {
            showAlert(data.error || 'Error deleting budget', 'danger');
            return;
        }

        showAlert('Budget deleted successfully');
        window.location.reload();
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error deleting budget', 'danger');
    }
}

function displayBudgetInTable(budget) {
    console.log('Displaying budget in table:', budget);

    const tableBody = document.getElementById('budgetTableBody');
    if (!tableBody) {
        console.error('Table body not found!');
        return;
    }

    if (!budget || !budget.amount) {
        console.log('No budget data available');
        tableBody.innerHTML = '<tr><td colspan="3" class="text-center">No budget set</td></tr>';
        return;
    }

    const formattedDate = budget.created_at
        ? formatDate(budget.created_at)
        : formatDate(new Date().toISOString());

    const rowHTML = `
        <tr>
            <td>₹${budget.amount.toFixed(2)}</td>
            <td>${formattedDate}</td>
            <td class="text-start">
                <button class="btn btn-sm btn-primary me-2" onclick="showUpdateModal('${budget._id}', ${budget.amount})">
                    Update
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteBudget('${budget._id}')">
                    Delete
                </button>
            </td>
        </tr>
    `;

    tableBody.innerHTML = rowHTML;
}

// Utility functions remain the same
function formatDate(isoString) {
    try {
        const datePart = isoString.split('T')[0];
        const [year, month, day] = datePart.split('-').map(Number);
        const date = new Date(year, month - 1, day);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (error) {
        console.error('Date error:', error);
        return new Date().toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
}

function showUpdateModal(budgetId, currentAmount) {
    document.getElementById('updateBudgetId').value = budgetId;
    document.getElementById('updateBudgetAmount').value = currentAmount;
    const updateModal = new bootstrap.Modal(document.getElementById('updateBudgetModal'));
    updateModal.show();
}

function updateSummaryCards(budget, totalExpenses) {
    const monthlyBudgetElement = document.querySelector('.card:nth-child(2) .fs-4');
    const remainingBudgetElement = document.querySelector('.card:nth-child(3) .fs-4');

    if (budget && budget.amount) {
        monthlyBudgetElement.textContent = `₹${budget.amount.toFixed(2)}`;
        const remaining = budget.amount - totalExpenses;
        remainingBudgetElement.textContent = `₹${remaining.toFixed(2)}`;

        remainingBudgetElement.classList.remove('text-success', 'text-primary', 'text-danger');
        remainingBudgetElement.classList.add(remaining < 0 ? 'text-danger' : 'text-success');
    } else {
        monthlyBudgetElement.textContent = '₹0.00';
        remainingBudgetElement.textContent = `₹${(-totalExpenses).toFixed(2)}`;
        remainingBudgetElement.classList.remove('text-success', 'text-primary');
        remainingBudgetElement.classList.add('text-danger');
    }
}
async function handleFilterSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const queryParams = new URLSearchParams(formData);
    window.location.href = `/dashboard?${queryParams.toString()}`;
}
</script>
{% endblock %}"""

with open("templates/dashboard.html", "w") as file:
    file.write(dashboard_html)

print("✅ Templates saved successfully!")

import os

os.makedirs("static", exist_ok=True)

# Save styles.css
styles_css = """/* General Styles */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8f9fa;
    color: #333;
}

/* Login & Register Pages */
.login-container {
    max-width: 400px;
    margin: 50px auto;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Dashboard Layout */
.dashboard {
    min-height: 100vh;
    background-color: #f8f9fa;
}

header {
    background-color: #2c3e50;
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Summary Cards */
.summary-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.summary-card h3 {
    color: #2c3e50;
}

.amount {
    font-size: 24px;
    font-weight: bold;
    color: #3498db;
}

/* Modal Styling */
.modal-content {
    border: none;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.modal-header {
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    padding: 1.25rem;
}

.modal-body {
    background-color: #fff;
}

.modal-footer {
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
    padding: 1rem 1.5rem;
}

/* Form Styling */
.form-label {
    color: #344767;
    margin-bottom: 0.5rem;
}

.form-control, .form-select {
    border: 1px solid #e9ecef;
    padding: 0.75rem;
    border-radius: 8px;
    transition: all 0.2s ease;
}

.form-control:focus, .form-select:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 0.2rem rgba(59, 130, 246, 0.25);
}

.input-group-text {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
}

/* Budget Overview */
.budget-item {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 10px;
}

/* Progress Bar */
.progress {
    height: 8px;
}

.progress-bar {
    background-color: #3498db;
}

/* Table */
.table {
    width: 100%;
    margin-top: 15px;
}

.table thead {
    background-color: #f8f9fa;
}


/* Button Styling */
.btn {
    padding: 0.625rem 1.25rem;
    font-weight: 500;
    border-radius: 8px;
    transition: all 0.2s ease;
}

.btn-primary {
    background-color: #3b82f6;
    border-color: #3b82f6;
}

.btn-primary:hover {
    background-color: #2563eb;
    border-color: #2563eb;
}

.btn-success {
    background-color: #10b981;
    border-color: #10b981;
}

.btn-success:hover {
    background-color: #059669;
    border-color: #059669;
}

.btn-logout {
    background-color: #e74c3c;
}

.btn-logout:hover {
    background-color: #c0392b;
}

/* Animation */
.modal.fade .modal-dialog {
    transform: scale(0.95);
    transition: transform 0.2s ease-out;
}

.modal.show .modal-dialog {
    transform: scale(1);
}

/* Alert Messages */
.alert {
    padding: 10px;
    border-radius: 4px;
}

/* Filter Section */
.filter-section form {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
}

/* Export Section */
.export-section {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
}

/* Responsive Design */
@media (max-width: 768px) {
    .main-content {
        padding: 10px;
    }

    header {
        flex-direction: column;
        gap: 10px;
        text-align: center;
    }

    .user-info {
        flex-direction: column;
    }
}"""

with open("static/styles.css", "w") as file:
    file.write(styles_css)

print("✅ Static saved successfully!")

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file, flash
from flask_pymongo import PyMongo
from flask_session import Session
from pyngrok import ngrok
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import io
import base64
from datetime import datetime
import certifi

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Change this to a secure secret key

# MongoDB Atlas Configuration
app.config["MONGO_URI"] = "mongodb+srv://safnaasadique:5juwG9maSknj7oKv@sample0.yu0df.mongodb.net/expense_tracker?retryWrites=true&w=majority&appName=Sample0"
mongo = PyMongo(app, tlsCAFile=certifi.where())

# Session Configuration
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Predefined categories
CATEGORIES = [
    "Food", "Transportation", "Housing", "Utilities","Groceries",
    "Entertainment", "Healthcare", "Shopping", "Other"
]

# User Registration and Authentication
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        # Check if username already exists
        if mongo.db.users.find_one({"username": username}):
            flash("Username already exists!", "error")
            return redirect(url_for("register"))

        # Create new user
        user = {
            "username": username,
            "password": generate_password_hash(password),
            "email": email,
            "created_at": datetime.utcnow()
        }
        mongo.db.users.insert_one(user)
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = mongo.db.users.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["logged_in"] = True
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid credentials!", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# Dashboard and Expense Management
@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    category_mapping = {
        "Food": {"color": "#FF6384", "order": 1},
        "Transportation": {"color": "#36A2EB", "order": 2},
        "Housing": {"color": "#FFCE56", "order": 3},
        "Utilities": {"color": "#4BC0C0", "order": 4},
        "Groceries": {"color": "#9966FF", "order": 5},
        "Entertainment": {"color": "#FF9F40", "order": 6},
        "Healthcare": {"color": "#EC6B56", "order": 7},
        "Shopping": {"color": "#FFC154", "order": 8},
        "Other": {"color": "#47B39C", "order": 9}
    }


    # Get user's expenses
    expenses = list(mongo.db.expenses.find({"user": session["username"]}))
    total_expenses = sum(expense['amount'] for expense in expenses)
    df = pd.DataFrame(expenses) if expenses else pd.DataFrame()

    all_categories = list(category_mapping.keys())
    category_totals = {category: 0 for category in all_categories}

    # Update with actual expense totals where they exist
    if not df.empty:
        expense_totals = df.groupby("category")["amount"].sum().to_dict()
        category_totals.update(expense_totals)

    # Create ordered lists for chart
    categories = all_categories  # All predefined categories
    amounts = [category_totals[cat] for cat in categories]  # Corresponding amounts (0 if no expenses)
    colors = [category_mapping[cat]["color"] for cat in categories]  # Corresponding colors

    # Get user's monthly budget
    monthly_budget_doc = mongo.db.budget.find_one({"user": session["username"], "category": "monthly"})
    monthly_budget = monthly_budget_doc['amount'] if monthly_budget_doc else 0

    # Calculate remaining budget
    remaining_budget = monthly_budget - total_expenses

    return render_template("dashboard.html",
        categories=categories,
        category_totals=amounts,
        category_colors=colors,
        expenses=expenses,
        monthly_budget=monthly_budget,
        total_expenses=total_expenses,
        remaining_budget=remaining_budget
    )

@app.route("/api/expenses/<expense_id>", methods=["GET"])
def get_expense(expense_id):
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        expense = mongo.db.expenses.find_one({"_id": ObjectId(expense_id), "user": session["username"]})
        if expense:
            expense["_id"] = str(expense["_id"])
            expense["date"] = expense["date"].strftime("%Y-%m-%d")
            return jsonify(expense)
        return jsonify({"error": "Expense not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/expenses", methods=["GET", "POST", "PUT", "DELETE"])
def handle_expenses():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "GET":
        filters = {"user": session["username"]}
        category = request.args.get("category")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if category:
            filters["category"] = category
        if start_date and end_date:
            filters["date"] = {
                "$gte": datetime.strptime(start_date, "%Y-%m-%d"),
                "$lte": datetime.strptime(end_date, "%Y-%m-%d")
            }

        expenses = list(mongo.db.expenses.find(filters))
        return jsonify([{**exp, "_id": str(exp["_id"])} for exp in expenses])

    if request.method == "POST":
        try:
            data = request.json
            # Validate required fields
            required_fields = ["name", "amount", "category", "date"]
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400

            # Convert string date to datetime object
            try:
                expense_date = datetime.strptime(data["date"], "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

            # Validate amount is a number
            try:
                amount = float(data["amount"])
                if amount <= 0:
                    return jsonify({"error": "Amount must be greater than 0"}), 400
            except ValueError:
                return jsonify({"error": "Invalid amount format"}), 400

            # Create expense document
            expense = {
                "name": data["name"],
                "amount": amount,
                "category": data["category"],
                "description": data.get("description", ""),
                "date": expense_date,
                "recurring": data.get("recurring", False),
                "user": session["username"],
                "created_at": datetime.utcnow()
            }

            # Insert expense into database
            result = mongo.db.expenses.insert_one(expense)

            if result.inserted_id:
                return jsonify({
                    "message": "Expense added successfully",
                    "id": str(result.inserted_id)
                }), 201
            else:
                return jsonify({"error": "Failed to insert expense"}), 500

        except Exception as e:
            return jsonify({"error": f"Error adding expense: {str(e)}"}), 500

    if request.method == "PUT":
        try:
            data = request.json
            expense_id = ObjectId(data["id"])

            # Validate date format
            try:
                expense_date = datetime.strptime(data["date"], "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

            # Validate amount
            try:
                amount = float(data["amount"])
                if amount <= 0:
                    return jsonify({"error": "Amount must be greater than 0"}), 400
            except ValueError:
                return jsonify({"error": "Invalid amount format"}), 400

            update_data = {
                "name": data["name"],
                "amount": amount,
                "category": data["category"],
                "description": data.get("description", ""),
                "date": expense_date,
                "updated_at": datetime.utcnow()
            }

            result = mongo.db.expenses.update_one(
                {"_id": expense_id, "user": session["username"]},
                {"$set": update_data}
            )

            if result.modified_count:
                return jsonify({"message": "Expense updated successfully"})
            return jsonify({"error": "Expense not found"}), 404
        except Exception as e:
            return jsonify({"error": f"Error updating expense: {str(e)}"}), 500

    if request.method == "DELETE":
        try:
            data = request.json
            expense_id = ObjectId(data["id"])
            result = mongo.db.expenses.delete_one({"_id": expense_id, "user": session["username"]})

            if result.deleted_count:
                return jsonify({"message": "Expense deleted successfully"})
            return jsonify({"error": "Expense not found"}), 404
        except Exception as e:
            return jsonify({"error": f"Error deleting expense: {str(e)}"}), 500

@app.route("/api/budget", methods=["GET", "POST", "PUT", "DELETE"])
def handle_budget():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "GET":
        budgets = list(mongo.db.budget.find({"user": session["username"]}))
        return jsonify([{**budget, "_id": str(budget["_id"])} for budget in budgets])

    if request.method == "POST":
        data = request.json
        budget = {
            "category": data["category"],
            "amount": float(data["amount"]),
            "user": session["username"],
            "created_at": datetime.utcnow()
        }
        result = mongo.db.budget.update_one(
            {"category": data["category"], "user": session["username"]},
            {"$set": budget},
            upsert=True
        )
        return jsonify({"message": "Budget updated successfully"})

    if request.method == "PUT":
        data = request.json
        budget = {
            "category": data["category"],
            "amount": float(data["amount"]),
            "user": session["username"],
            "created_at": datetime.utcnow()
        }
        result = mongo.db.budget.update_one(
            {"category": data["category"], "user": session["username"]},
            {"$set": budget},
            upsert=True
        )
        return jsonify({"message": "Budget updated successfully"})

    if request.method == "DELETE":
        data = request.json
        budget_id = ObjectId(data["id"])
        result = mongo.db.budget.delete_one({"_id": budget_id, "user": session["username"]})
        if result.deleted_count:
            return jsonify({"message": "Budget deleted successfully"})
        return jsonify({"error": "Budget not found"}), 404

@app.route("/api/chart")
def get_chart():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    # Define all categories and colors
    category_mapping = {
        "Food": {"color": "#FF6384", "order": 1},
        "Transportation": {"color": "#36A2EB", "order": 2},
        "Housing": {"color": "#FFCE56", "order": 3},
        "Utilities": {"color": "#4BC0C0", "order": 4},
        "Groceries": {"color": "#9966FF", "order": 5},
        "Entertainment": {"color": "#FF9F40", "order": 6},
        "Healthcare": {"color": "#EC6B56", "order": 7},
        "Shopping": {"color": "#FFC154", "order": 8},
        "Other": {"color": "#47B39C", "order": 9}
    }

    expenses = list(mongo.db.expenses.find({"user": session["username"]}))

    # Initialize all categories with 0 values
    all_categories = list(category_mapping.keys())
    category_totals = {category: 0 for category in all_categories}

    # Update with actual expense totals
    if expenses:
        df = pd.DataFrame(expenses)
        expense_totals = df.groupby("category")["amount"].sum().to_dict()
        category_totals.update(expense_totals)

    # Create lists for chart
    categories = all_categories
    amounts = [category_totals[cat] for cat in categories]
    colors = [category_mapping[cat]["color"] for cat in categories]

    # Create pie chart (only for categories with non-zero amounts)
    plt.figure(figsize=(10, 10))
    non_zero_indices = [i for i, amount in enumerate(amounts) if amount > 0]

    if non_zero_indices:  # If there are any expenses
        plt.pie([amounts[i] for i in non_zero_indices],
                labels=[categories[i] for i in non_zero_indices],
                colors=[colors[i] for i in non_zero_indices],
                autopct='%1.1f%%')
    else:  # If no expenses, show empty chart
        plt.pie([1], labels=['No expenses'], colors=['#CCCCCC'])

    plt.title("Expense Distribution by Category")

    # Save chart to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    chart_data = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return jsonify({"chart": f"data:image/png;base64,{chart_data}"})

@app.route("/export_data")
def export_data():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    export_format = request.args.get("format", "csv")
    expenses = list(mongo.db.expenses.find({"user": session["username"]}, {"_id": 0}))

    if export_format == "csv":
        df = pd.DataFrame(expenses)
        output = io.StringIO()
        df.to_csv(output, index=False)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='expenses.csv'
        )

    elif export_format == "pdf":
        # Create PDF using ReportLab
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Convert expenses to table data
        data = [[
            "Name", "Amount", "Category", "Date", "Description", "Recurring"
        ]]
        for expense in expenses:
            data.append([
                expense["name"],
                f"₹{expense['amount']:.2f}",
                expense["category"],
                expense["date"].strftime("%Y-%m-%d"),
                expense.get("description", ""),
                "Yes" if expense.get("recurring") else "No"
            ])

        # Create table and style it
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='expenses.pdf'
        )

if __name__ == "__main__":
    try:
        ngrok.set_auth_token("2tDYsTBOAuoN3eGOm3ESzM78rJF_6LHaHkj7esZa5xY1p1xi1")
        public_url = ngrok.connect(5000).public_url
        print(f"\n🔗 Ngrok Public URL: {public_url}")
        print("✨ Use this URL to access your expense tracker login page!")
    except Exception as e:
        print(f"\n❌ Error setting up ngrok: {str(e)}")
        print("🔧 The application will still run locally at http://localhost:5000")

    app.run(port=5000)

!fuser -k 5000/tcp

!ps aux | grep ngrok

!killall ngrok

!apt-get update
!apt-get install -y git
!pip install PyGithub

from github import Github
from datetime import datetime
from google.colab import drive
import json
import os
import nbformat
import shutil

class EnhancedGitHubManager:
    def __init__(self):
        """Initialize manager without credentials"""
        self.github = None
        self.repo = None
        self.mount_drive()
        self.base_folder_name = "Expense_Tracker"

    def mount_drive(self):
        """Mount Google Drive if not already mounted"""
        if not os.path.exists('/content/drive'):
            drive.mount('/content/drive')

    def get_github_credentials(self):
        """Get GitHub credentials from secure file"""
        creds_file = "/content/drive/MyDrive/.secure_credentials/github_creds.json"
        try:
            with open(creds_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Credentials file not found!")
            return None
        except json.JSONDecodeError:
            print("Error reading credentials file!")
            return None

    def initialize_github(self):
        """Initialize GitHub connection with credentials"""
        creds = self.get_github_credentials()
        if creds:
            github_token = creds.get('github_token')
            github_username = creds.get('github_username')

            if github_token and github_username:
                self.github = Github(github_token)
                repo_name = f"{github_username}/Expense_Tracker"
                try:
                    self.repo = self.github.get_repo(repo_name)
                    print(f"Successfully connected to repository: {repo_name}")
                    return True
                except Exception as e:
                    print(f"Error connecting to repository: {str(e)}")
                    return False
        return False

    def get_next_version_number(self):
        """Get the next available version number"""
        if not self.repo:
            return 1

        try:
            contents = self.repo.get_contents("")
            existing_versions = []

            for content in contents:
                if content.type == "dir" and content.name.startswith(self.base_folder_name + "_v"):
                    version_num = int(content.name.split('v')[-1])
                    existing_versions.append(version_num)

            if not existing_versions:
                return 1
            return max(existing_versions) + 1
        except Exception as e:
            print(f"Error getting next version number: {str(e)}")
            return 1

    def extract_python_code(self, notebook_path):
        """Extract Python code from Jupyter Notebook"""
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)

            python_code = []
            for cell in nb.cells:
                if cell.cell_type == "code":
                    python_code.append(cell.source.strip())

            return "\n\n".join(python_code)
        except Exception as e:
            print(f"Error extracting Python code: {str(e)}")
            return None

    def create_version_folder(self, version_number):
        """Create a new version folder and copy files into it"""
        version_folder = f"{self.base_folder_name}_v{version_number}"

        # Remove old version folder if it exists locally
        if os.path.exists(version_folder):
            shutil.rmtree(version_folder)

        # Create new folder structure
        os.makedirs(os.path.join(version_folder, "templates"), exist_ok=True)
        os.makedirs(os.path.join(version_folder, "static"), exist_ok=True)
        os.makedirs(os.path.join(version_folder, "python_code"), exist_ok=True)

        return version_folder

    def save_extracted_content(self, version_number):
        """Save extracted HTML, CSS, and Python code to version-specific folder"""
        version_folder = self.create_version_folder(version_number)

        # Copy HTML files from template folder
        template_path = "/content/templates"
        html_files = ["base.html", "dashboard.html", "login.html", "register.html"]
        for file in html_files:
            src_file = os.path.join(template_path, file)
            dest_file = os.path.join(version_folder, "templates", file)
            if os.path.exists(src_file):
                with open(src_file, "r", encoding="utf-8") as f:
                    content = f.read()
                with open(dest_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Saved: {file} to version {version_number}")

        # Copy CSS file from static folder
        css_file = "/content/static/styles.css"
        if os.path.exists(css_file):
            with open(css_file, "r", encoding="utf-8") as f:
                content = f.read()
            with open(os.path.join(version_folder, "static", "styles.css"), "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Saved: styles.css to version {version_number}")

        # Extract and save Python code
        python_code = self.extract_python_code("/content/drive/MyDrive/Colab Notebooks/Final Project - Expense Tracker.ipynb")
        if python_code:
            with open(os.path.join(version_folder, "python_code", "main.py"), "w", encoding="utf-8") as f:
                f.write(python_code)
            print(f"Saved: main.py to version {version_number}")

        return version_folder

    def upload_version_folder(self, version_folder):
        """Upload a specific version folder to GitHub"""
        if not self.repo:
            print("GitHub repository not initialized!")
            return False

        try:
            for root, dirs, files in os.walk(version_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Create GitHub path relative to repo root
                    repo_path = file_path.replace("\\", "/")

                    try:
                        # Try to create new file
                        self.repo.create_file(repo_path, f"Added {file} to {version_folder}", content)
                        print(f"Uploaded: {file} to {version_folder}")
                    except Exception as e:
                        print(f"Error uploading {file}: {str(e)}")
            return True
        except Exception as e:
            print(f"Error uploading version folder: {str(e)}")
            return False

    def list_versions(self):
        """List all versions with their files"""
        if not self.repo:
            print("GitHub repository not initialized!")
            return []

        try:
            contents = self.repo.get_contents("")
            versions = []

            for content in contents:
                if content.type == "dir" and content.name.startswith(self.base_folder_name + "_v"):
                    version_files = []
                    self._get_files_recursively(content.path, version_files)

                    version_info = {
                        'version': content.name,
                        'files': version_files,
                        'created_at': self.repo.get_commits(path=content.path)[0].commit.author.date
                    }
                    versions.append(version_info)

            # Sort versions by number
            versions.sort(key=lambda x: int(x['version'].split('v')[-1]))

            print("\nExisting versions in repository:")
            print("-" * 50)
            for version in versions:
                print(f"Version: {version['version']}")
                print(f"Created: {version['created_at']}")
                print("Files:")
                for file in version['files']:
                    print(f"  - {file}")
                print("-" * 50)

            return versions

        except Exception as e:
            print(f"Error listing versions: {str(e)}")
            return []

    def _get_files_recursively(self, path, files_list):
        """Helper method to recursively get all files in a directory"""
        contents = self.repo.get_contents(path)
        for content in contents:
            if content.type == "dir":
                self._get_files_recursively(content.path, files_list)
            else:
                files_list.append(content.path)

def main():
    """Main function to create and upload a single version"""
    manager = EnhancedGitHubManager()

    if manager.initialize_github():
        # Get the next available version number
        next_version = manager.get_next_version_number()
        print(f"\nCreating Version {next_version}")
        print("-" * 30)

        # Save content to version-specific folder
        version_folder = manager.save_extracted_content(next_version)

        # Upload the version folder
        if manager.upload_version_folder(version_folder):
            print(f"Successfully uploaded version {next_version}")
        else:
            print(f"Failed to upload version {next_version}")

        # Clean up local version folder
        shutil.rmtree(version_folder)

        # List all versions after upload
        manager.list_versions()
    else:
        print("Failed to initialize GitHub connection")

if __name__ == "__main__":
    main()