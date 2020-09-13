from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


app.secret_key = "super secret key"

@app.route('/')
def home():
    """This is the entry point of the application
    :return
        Render index.html
    """
    return render_template('index.html')

@app.route('/settings')
def settings():
    """This is the setting page of the application
    in this page the user can setup his preferences such as:
    passwords email address...
    """
    return render_template('settings.html')

@app.route('/project')
def project():
    """
    
    """
    return render_template('project.html')


if __name__ == "__main__":
    app.run(debug=True)
