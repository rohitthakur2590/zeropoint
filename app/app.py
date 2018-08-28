import os
from datetime import datetime
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_bootstrap import Bootstrap
import secrets
from PIL import Image


from lxml.etree import XMLSyntaxError
from lxml.etree import tostring
from xml.etree  import ElementTree as ET

from wtforms import Form, TextAreaField, validators, SubmitField, TextField
from wtforms.validators import InputRequired, DataRequired

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
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
	firstname = db.Column(db.String(20))
	lastname = db.Column(db.String(20))
	username = db.Column(db.String(50), unique=True)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	email = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(80))
	posts = db.relationship('Post', backref='author', lazy=True)

class Post(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))



#Login Form
class LoginForm(FlaskForm):
      email = StringField('email', validators=[InputRequired(), Length(min=4, max=50)])
      password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
      remember = BooleanField('remember me')

#Register Form
class RegisterForm(FlaskForm): 
      firstname = StringField('First name', validators=[InputRequired(), Length(min=1, max=20)])
      lastname = StringField('Last name', validators=[InputRequired(), Length(min=1, max=20)])
      email = StringField('Email-Id', validators=[InputRequired(), Email(message = 'Invalid email'), Length(max=50)])
      password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

class UpdateProfileForm(FlaskForm): 
      firstname = StringField('First name', validators=[InputRequired(), Length(min=1, max=20)])
      lastname = StringField('Last name', validators=[InputRequired(), Length(min=1, max=20)])
      username = StringField('Username', validators=[InputRequired(), Length(min=1, max=20)])
      email = StringField('Email-Id', validators=[InputRequired(), Email(message = 'Invalid email'), Length(max=50)])
      picture = FileField('Update Display Picture', validators=[FileAllowed(['jpg', 'png'])])
      #submit = SubmitField('Update')

      def validate_username(self, username):
      	if username.data != current_user.username:
      		user = User.query.filter_by(username=username.data).first()
      		if user:
      			raise ValidationError('username is already taken')

      def validate_email(self, email):
      	if email.data != current_user.email:
      		user = User.query.filter_by(username=email.data).first()
      		if user:
      			raise ValidationError('email account already exist')

class CommandToSendForm(Form):
        fixedXmlString = TextAreaField("Fixed XML String",render_kw={'class': 'form-control','readonly': True})
        command = TextAreaField("Command to Send", [InputRequired("Please enter a command!")],render_kw={'class': 'form-control'})
        send = SubmitField(label='Send')
        btn_template = SubmitField()

class OutputForm(Form):
        copy = SubmitField(label='Copy Output')
        output = TextAreaField("Received Output",render_kw={'class': 'form-control'}) 

class PostForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Content', validators=[DataRequired()])
	#submit = SubmitField('Post')






@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		#looking for user in database
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('dashboard'))
		flash('Invalid username or password!', category='danger')
		return render_template('login.html', form=form)
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
 		new_user = User(firstname=form.firstname.data, 
 			            lastname=form.lastname.data,
 			            email=form.email.data, 
 			            password=hash_password)

 		db.session.add(new_user)
 		db.session.commit()
 		flash(f'Sign Up successful for {form.firstname.data}!', 'success')
 		return render_template('index.html')
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
	return render_template('dashboard.html', name=current_user.firstname)	


@app.route('/profile')
@login_required
def profile():
	form = UpdateProfileForm()
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)	
	return render_template('profile.html', name=current_user.firstname, image_file=img_file, form=form)	

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex+ f_ext
	picture_path = os.path.join(app.root_path, 'static/display_pics', picture_fn)

	output_size = (200, 200)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = UpdateProfileForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file

		current_user.firstname = form.firstname.data
		current_user.lastname = form.lastname.data
		current_user.username = form.username.data
		current_user.email= form.email.data
		db.session.commit()
		flash('Profile Updated Successfully', 'success')
		return redirect(url_for('profile'))
	elif request.method == 'GET':
		form.firstname.data = current_user.firstname
		form.lastname.data = current_user.lastname
		form.username.data = current_user.username
		form.email.data = current_user.email
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)	
	return render_template('edit_profile.html', name=current_user.firstname, image_file=img_file, form=form)	



@app.route('/my_blog', methods=['GET', 'POST'])
@login_required
def my_blog():
	form = PostForm()

	if form.validate_on_submit():
		post= Post(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!', 'success')
		return redirect(url_for('profile'))
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('my_blog.html', image_file=img_file, form=form)

@app.route('/blog_home', methods=['GET', 'POST'])
@login_required
def blog_home():
	posts= Post.query.all()
	img_file = url_for('static', filename='display_pics/' + current_user.image_file)
	return render_template('blog_home.html', image_file=img_file, posts=posts)

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