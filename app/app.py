from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap

from lxml.etree import XMLSyntaxError
from lxml.etree import tostring
from xml.etree  import ElementTree as ET

from wtforms import Form, TextAreaField, validators, SubmitField, TextField
from wtforms.validators import InputRequired

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length 
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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

'''
flask uses UserMixin to injectsome extra thing to user 
'''

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique=True)
	email = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(80))
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))



#Login Form
class LoginForm(FlaskForm):
      username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
      password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
      remember = BooleanField('remember me')

#Register Form
class RegisterForm(FlaskForm):
      email = StringField('email', validators=[InputRequired(), Email(message = 'Invalid email'), Length(max=50)])
      username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
      password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

class CommandToSendForm(Form):
        fixedXmlString = TextAreaField("Fixed XML String",render_kw={'class': 'form-control','readonly': True})
        command = TextAreaField("Command to Send", [InputRequired("Please enter a command!")],render_kw={'class': 'form-control'})
        send = SubmitField(label='Send')
        btn_template = SubmitField()

class OutputForm(Form):
        copy = SubmitField(label='Copy Output')
        output = TextAreaField("Received Output",render_kw={'class': 'form-control'}) 
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		#looking for user in database
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('dashboard'))

		return '<h1>Invalid username or password</h1>'
		#return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
	return render_template('login.html', form=form)
'''
sha256 will generate 80 characters long password
'''
@app.route('/signup', methods=['GET', 'POST'])
def signup():
 	form = RegisterForm()

 	if form.validate_on_submit():
 		hash_password = generate_password_hash(form.password.data, method='sha256')
 		new_user = User(username=form.username.data, email=form.email.data, password=hash_password)
 		db.session.add(new_user)
 		db.session.commit()

 		return '<h1>You Have Registered Successfully!</h1>'
 		#return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

 	return render_template('signup.html', form=form)


@app.route('/notepad', methods=['GET', 'POST'])
@login_required
def notepad():
	#form for input notes
	form = CommandToSendForm()
	outputform = OutputForm()

	command = ""
    
	#parse button_input.xml
	buttons = parse_buttons()
	button_list = sorted(buttons.items())
	if request.method == 'POST' :
		if 'btn_template' in request.form:
			command = read_command_template(request, buttons)
			#set command into command box
			form.command.data = command
		if 'save' in request.form:
			command = request.form['command'].encode('utf-8')

		return render_template('notepad.html',
    		                    command = command,
    		                    buttons=buttons_list,
    		                    form=form,
    		                    output=output.xml,
    		                    outputform=outputform)

	return render_template('notepad.html', form=form,  outputform=outputform)

def parse_buttons():
	XMLtree = ET.parse('button_template/button_config.xml')
	root = XMLtree.getroot()
	button = {}
	for button in root.findall('button'):
		title = button.find('title')
		button[0] = render_template
	return button

@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html', name=current_user.username)	

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)












'''
#Setup the Database
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
#instantiate app
app = Flask(__name__)

#Configure the database
#app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:////sqlite:////C:/Users/HP/Desktop/evora/evainit/venv/app/evaidsite.db'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///evaidsite.db'
app.config['SECRET_KEY'] = 'secret'

#instantiate database
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

#create User class that represent the databse on table
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(30), unique=True)


create a function that flask login  will use to connect tha abstrcat user
with actual user 

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/')
def index():
	user = User.query.filter_by(username='Rohit').first()

if __name__ == '__main__':
	app.
'''