import os
from flask import Flask, render_template, request, redirect, session
from flask_session import Session

# custom library
from helpers import apology, login_required
from stamp import RegFormStamper

current_dir = os.path.dirname(os.path.abspath(__file__))

template_folder_path = os.path.join(current_dir, '..', 'frontend', 'templates')
static_folder_path = os.path.join(current_dir, '..', 'frontend', 'static')

app = Flask(__name__,
            template_folder=template_folder_path,
            static_folder=static_folder_path)

# Server side sessions
app.config["SESSION_PERMANENT"] = False     # Sessions expire when the browser is closed
app.config["SESSION_TYPE"] = "filesystem"       # Set to "filesystem" so that session data is stored on the server's disk

# Initialize Flask-Session
Session(app)

pdf_path = os.path.join(static_folder_path, 'assets', 'RC-UPI-01_Application-for-Crop-Insurance.pdf')
stamper = RegFormStamper(pdf_path)

# asset path
assets_base_path = os.path.join(static_folder_path, 'assets')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # If user is already logged in, redirect them away from login page
    if "email" in session:
        return redirect("/admin/dashboard")

    # If a user is submitting the login form
    if request.method == "POST":
        # Auto-login for prototype - no validation needed
        demo_email = "demo@lgu.gov.ph"
        session["email"] = demo_email
        return redirect("/admin/dashboard")

    # GET request
    return render_template("login.html")

@app.route("/farmer-login", methods=["GET", "POST"])
def farmer_login():
    """Log farmer in"""
    # If farmer is already logged in, redirect them away from login page
    if "farmer_username" in session:
        return redirect("/farmer/dashboard")

    # If a farmer is submitting the login form
    if request.method == "POST":
        # Auto-login for prototype - no validation needed
        demo_username = "juan_delacruz"
        session["farmer_username"] = demo_username
        return redirect("/farmer/dashboard")

    # GET request - redirect back to main login page
    return redirect("/login")

@app.route("/farmer/dashboard")
def farmer_dashboard():
    """Farmer dashboard"""
    username = session.get("farmer_username", "juan_delacruz")
    return render_template("farmer/dashboard.html", username=username)

@app.route("/farmer/insurance-status")
def farmer_insurance_status():
    """Farmer insurance status"""
    username = session.get("farmer_username", "juan_delacruz")
    return render_template("farmer/insurance-status.html", username=username)

@app.route("/farmer/documents")
def farmer_documents():
    """Farmer documents"""
    username = session.get("farmer_username", "juan_delacruz")
    return render_template("farmer/documents.html", username=username)

@app.route("/farmer/transaction-history")
def farmer_transaction_history():
    """Farmer transaction history"""
    username = session.get("farmer_username", "juan_delacruz")
    return render_template("farmer/transaction-history.html", username=username)

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if request.method == "POST":
        pass
    # email = session.get("email", "demo@lgu.gov.ph")
    return render_template("admin/dashboard.html")

@app.route("/admin/register-farm", methods=["GET", "POST"])
@login_required
def admin_register_farm():
    return render_template("admin/register-farm.html")

@app.route("/admin/damage-assessment")
@login_required
def admin_damage_assessment():
    return render_template("admin/damage-assessment.html")

@app.route("/admin/farmers")
@login_required
def admin_farmers():
    return render_template("admin/farmers.html")

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear() # Clear session data
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)