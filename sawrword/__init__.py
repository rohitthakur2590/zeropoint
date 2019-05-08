from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

#instantiate app
app = Flask(__name__)
#set secret key value
app.config['SECRET_KEY']   = 'evaidsecret'
#Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///evadatabase.db'
Bootstrap(app)
#initialize db
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] ='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sawrword@gmail.com'
app.config['MAIL_PASSWORD'] = 'sawrword_1618'
mail = Mail(app)



from sawrword import routes


