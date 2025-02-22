!pip install flask flask-sqlalchemy flask-session flask-pymongo flask-pyngrok pymongo dnspython reportlab flask-ngrok

!pip install "pymongo[srv]" dnspython

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
from pathlib import Path
import re
import nbformat
import base64

class NotebookWebVersionManager:
    def __init__(self):
        """Initialize manager without credentials"""
        self.github = None
        self.repo = None
        self.mount_drive()

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

    def extract_content(self, notebook_path):
        """
        Extract HTML, CSS, JavaScript and Python content from notebook cells
        Returns a dictionary containing separated content
        """
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)

            content = {
                'html': [],
                'css': [],
                'javascript': [],
                'python': []
            }

            for cell in nb.cells:
                if cell.cell_type == "code":
                    source = cell.source

                    # Extract HTML content
                    html_matches = re.findall(r'(?:html\s*=\s*)?"""(<!DOCTYPE html>[\s\S]*?|<html>[\s\S]*?)</html>"""', source)
                    template_matches = re.findall(r'(?:_html\s*=\s*)?"""(?:\s*{%[\s\S]*?%}[\s\S]*?){1,}"""', source)
                    if html_matches or template_matches:
                        content['html'].extend(html_matches)
                        content['html'].extend(template_matches)
                        continue

                    # Extract CSS content
                    css_matches = re.findall(r'(?:styles_css|css|style|styles)\s*=\s*[\'"]?([\s\S]*?)[\'"]?\s*(?:$|[;\n])', source)
                    css_multiline = re.findall(r'(?:styles_css|css|style|styles)\s*=\s*"""([\s\S]*?)"""', source)

                    if css_matches or css_multiline:
                        content['css'].extend(css_matches)
                        content['css'].extend(css_multiline)
                        continue

                    # Extract JavaScript content
                    js_matches = re.findall(r'(?:javascript|js)\s*=\s*"""([\s\S]*?)"""', source)
                    if js_matches:
                        content['javascript'].extend(js_matches)
                        continue

                    # If none of the above, it's Python code
                    content['python'].append(source)

            print("Extracted content summary:")
            print(f"HTML: {len(content['html'])} blocks")
            print(f"CSS: {len(content['css'])} blocks")
            print(f"JavaScript: {len(content['javascript'])} blocks")
            print(f"Python: {len(content['python'])} blocks")

            return content

        except Exception as e:
            print(f"Error extracting content: {str(e)}")
            return None

    def create_directory_structure(self, version_num, content):
        """
        Create directory structure for the version with separate files
        Returns a dictionary of file paths and their content
        """
        base_name = "expense_tracker"
        version_dir = f"{base_name}_v{version_num}"

        files = {}

        # Create HTML file
        if content['html']:
            html_content = "\n\n".join(content['html'])
            files[f"{version_dir}/templates/index.html"] = html_content

        # Create CSS file
        css_content = "\n\n".join(content['css']) if content['css'] else "/* Default styles */"
        files[f"{version_dir}/static/css/styles.css"] = css_content

        # Create JavaScript file
        if content['javascript']:
            js_content = "\n\n".join(content['javascript'])
            files[f"{version_dir}/static/js/script.js"] = js_content

        # Create Python file
        if content['python']:
            py_content = "\n\n".join(content['python'])
            files[f"{version_dir}/src/main.py"] = py_content

        return files

    def save_new_version(self, notebook_path, commit_message=None):
        """Save new version with proper directory structure to GitHub"""
        if not self.repo:
            print("GitHub repository not initialized!")
            return None

        try:
            # Extract content
            content = self.extract_content(notebook_path)
            if not content:
                print("No content found in notebook!")
                return None

            # Get version number
            version_num = self.get_existing_versions() + 1

            # Create directory structure
            files = self.create_directory_structure(version_num, content)

            if not commit_message:
                commit_message = f"Version {version_num} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # Save all files to GitHub
            for file_path, file_content in files.items():
                try:
                    # Check if file exists
                    try:
                        existing_file = self.repo.get_contents(file_path)
                        # Update existing file
                        self.repo.update_file(
                            file_path,
                            commit_message,
                            file_content,
                            existing_file.sha,
                            branch='main'
                        )
                    except:
                        # Create new file
                        self.repo.create_file(
                            file_path,
                            commit_message,
                            file_content,
                            branch='main'
                        )
                except Exception as e:
                    print(f"Error saving file {file_path}: {str(e)}")

            print(f"Successfully saved version {version_num}")
            return {
                'version': version_num,
                'files': list(files.keys()),
                'commit_message': commit_message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            print(f"Error saving to GitHub: {str(e)}")
            return None

    def get_existing_versions(self):
        """Get count of existing versions in the repository"""
        if not self.repo:
            print("GitHub repository not initialized!")
            return 0

        try:
            contents = self.repo.get_contents("")
            version_count = 0
            for content in contents:
                if content.type == "dir" and content.name.startswith("expense_tracker_v"):
                    try:
                        version_num = int(content.name.split('_v')[1])
                        version_count = max(version_count, version_num)
                    except:
                        continue
            return version_count
        except Exception as e:
            print(f"Error checking versions: {str(e)}")
            return 0

    def list_versions(self):
        """List all versions with their files"""
        if not self.repo:
            print("GitHub repository not initialized!")
            return []

        try:
            contents = self.repo.get_contents("")
            versions = []

            for content in contents:
                if content.type == "dir" and content.name.startswith("expense_tracker_v"):
                    version_files = self.repo.get_contents(content.path)
                    version_info = {
                        'version': content.name,
                        'files': [f.path for f in version_files],
                        'created_at': self.repo.get_commits(path=content.path)[0].commit.author.date
                    }
                    versions.append(version_info)

            print("\nVersions of web content:")
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

# Example usage
if __name__ == "__main__":
    manager = NotebookWebVersionManager()

    if manager.initialize_github():
        result = manager.save_new_version(
            "/content/drive/MyDrive/Colab Notebooks/Final Project - Expense Tracker.ipynb",
            "Initial version of expense tracker"
        )

        if result:
            manager.list_versions()