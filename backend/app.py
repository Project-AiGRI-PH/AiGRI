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
 
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    # email = session.get("email", "demo@lgu.gov.ph")
    return render_template("/admin/dashboard.html")

# To do: POST method action for
@app.route("/admin/insurance-application", methods=["GET", "POST"])
@login_required
def admin_insurance_application():
    if request.method == "POST":   
        form_fields = [
            "farm_sitio_1", "farm_barangay_1", "farm_municipality_1", "farm_north_1", "farm_south_1", "farm_east_1", "farm_west_1", "farm_variety_1",
        ]
        
        data = {
            "farmer_last": "DELA CRUZ",
            "farmer_first": "JUAN",
            "farmer_middle": "SANTOS",
            "farmer_sitio": "Sitio 1",
            "farmer_barangay": "Barangay 2",
            "farmer_municipality": "Municipality 3",
            "farmer_province": "Province 4",
            "farmer_cell": "09123456789",
            "farmer_bank name": "LandBank of the Philippines",
            "farmer_bank account No.": "12345",
            "farmer_bank branch / address": "Cebu City",
            "farm_province": "Leyte"
        }

        for field in form_fields:
            value = request.form.get(field)
            data[field] = value
        
        # Use context manager - automatic cleanup
        with RegFormStamper(pdf_path) as stamper:
            stamper.text_search(7, data, "../frontend/static/assets/stamped-sample-method1.pdf")

        return redirect("/admin/dashboard")
    
    return render_template("/admin/insurance-application.html")

@app.route("/admin/damage-assessment")
@login_required
def admin_damage_assessment():
    return render_template("/admin/damage-assessment.html")

@app.route("/admin/farmers")
@login_required
def admin_farmers():
    return render_template("/admin/farmers.html")

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear() # Clear session data
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)