import os
from flask import Flask, render_template, request, redirect, session
from flask_session import Session

# custom library
from helpers import apology, login_required

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
    email = session.get("email", "demo@lgu.gov.ph")
    return render_template("admin/dashboard.html", email=email)

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear() # Clear session data
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)