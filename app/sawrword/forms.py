from flask_login import current_user
from wtforms import Form, TextAreaField, validators, SubmitField, TextField
from wtforms.validators import InputRequired, DataRequired

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo, ValidationError

from sawrword.models import User

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

class RequestResetForm(FlaskForm):
  email = StringField('Email-Id', validators=[InputRequired(), Email(message = 'Invalid email'), Length(max=50)])
  submit = SubmitField('Request Password Reset')

  def validate_email(self, email):
          user = User.query.filter_by(email=email.data).first()
          if user is None:
            raise ValidationError('Email not registered.Want to create New account ?')

class ResetPasswordForm(FlaskForm):
  password = PasswordField('Password', validators=[DataRequired()])
  confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

  submit = SubmitField('Reset Password')
