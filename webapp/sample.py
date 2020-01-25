from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "<span style='color:red'>File in webapp dir 001</span>"



