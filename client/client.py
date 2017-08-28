from flask import Flask
app = Flask(__name__, static_folder='static', static_url_path='', template_folder='static')
app.debug=True