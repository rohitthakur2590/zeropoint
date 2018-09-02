from flask import Flask 
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

#instantiate app 
app = Flask(__name__)
#set secret key value
app.config['SECRET_KEY']   = 'evaidsecret' 
#Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///evadatabase.db' 
Bootstrap(app)
#initialize db
db = SQLAlchemy(app)
from sawrword import routes
