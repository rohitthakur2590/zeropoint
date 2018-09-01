import os
from flask import Flask 
from flask_bootstrap import Bootstrap
import secrets

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user,login_required, logout_user, current_user


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
