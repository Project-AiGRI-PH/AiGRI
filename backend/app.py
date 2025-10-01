import os
import cv2

from flask import Flask, render_template, request, redirect, session
from flask_session import Session

# custom library
from helpers import apology, login_required
from stamp import RegFormStamper
from farmland_damage_assessment import FarmlandDamageAssessor

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
damage_ass = FarmlandDamageAssessor()

# asset path
assets_base_path = os.path.join(static_folder_path, 'assets')

@app.route("/")
def index():
    # If user is already logged in, redirect accordingly
    if "email" in session:
        return redirect("/admin/dashboard")
    if "username" in session:
        return redirect("/farmer/dashboard")

    return render_template("index.html")

@app.route("/login")
def login():
    """Generic login page"""
    # If user is already logged in, redirect accordingly
    if "email" in session:
        return redirect("/admin/dashboard")
    if "username" in session:
        return redirect("/farmer/dashboard")

    return render_template("login.html")


@app.route("/admin/login", methods=["POST"])
def admin_login():
    if request.method == "POST":
        demo_email = "demo@lgu.gov.ph"
        session["email"] = demo_email
        return redirect("/admin/dashboard")

    return redirect("/login")


@app.route("/farmer/login", methods=["POST"])
def farmer_login():
    if request.method == "POST":
        demo_username = "juan"
        session["username"] = demo_username
        return redirect("/farmer/dashboard")

    return redirect("/login")

# ADMIN SIDE
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
        
        # Context manager - automatic cleanup
        with RegFormStamper(pdf_path) as stamper:
            stamper.text_search(7, data, "../frontend/static/assets/stamped-sample-method1.pdf")

        return redirect("/admin/dashboard")
    
    return render_template("/admin/insurance-application.html")

@app.route("/admin/damage-assessment", methods=["GET", "POST"])
@login_required
def admin_damage_assessment():
    if request.method == "POST":
        import matplotlib
        matplotlib.use('Agg')  # Set backend before any plotting
        
        # Define input image path
        image_path = "../frontend/static/assets/test_input/farm1.png"
        output_dir = "../frontend/static/assets/output/"

        os.makedirs(output_dir, exist_ok=True)

        # Output file paths
        report_output_path = os.path.join(output_dir, "farmland_damage_report.png")
        map_output_path = os.path.join(output_dir, "damage_map_only.png")

        if not os.path.exists(image_path):
            print("="*60)
            print("ERROR: Image file not found!")
            print("="*60 + "\n")
        else:
            try:
                damage_map, statistics = damage_ass.assess_damage(
                    image_path=image_path, 
                    output_path=report_output_path
                )
                
                cv2.imwrite(map_output_path, cv2.cvtColor(damage_map, cv2.COLOR_RGB2BGR))
                print("Success!!!")
            except Exception as e:
                print("="*60)
                print(e)
                print("=*60")

    return render_template("/admin/damage-assessment.html")

@app.route("/admin/farmers")
@login_required
def admin_farmers():
    return render_template("/admin/farmers.html")

# FARMER SIDE
@app.route("/farmer/dashboard")
@login_required
def farmer_dashboard():
    """Farmer dashboard"""
    username = session.get("farmer_username", "juan_delacruz")
    return render_template("farmer/dashboard.html", username=username)

@app.route("/farmer/insurance-status")
@login_required
def farmer_insurance_status():
    return render_template("/farmer/insurance-status.html")

@app.route("/farmer/profile")
@login_required
def farmer_profile():
    return render_template("/farmer/profile.html")

@app.route("/farmer/documents")
@login_required
def farmer_documents():
    return render_template("/farmer/documents.html")

@app.route("/farmer/payout-history")
@login_required
def farmer_payout_history():
    return render_template("/farmer/payout-history.html")

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear() # Clear session data
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)