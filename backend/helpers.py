# Cp from CS50x Finance helpers.py
from functools import wraps
from flask import request, redirect, render_template, session

# Flask decorator
# A decorator is a function that wraps and replaces another function
# Since the original function is replaced, you need to remember to copy the original function’s information to the new function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('email') is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    # Claude msg: When you return a tuple from a Flask route, Flask interprets it as (response, status_code)
    return render_template("apology.html", top=code, bottom=escape(message)), code