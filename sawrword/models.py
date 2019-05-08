from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from sawrword import db, app
from PIL import Image
from flask_login import UserMixin


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	firstname = db.Column(db.String(20))
	lastname = db.Column(db.String(20))
	username = db.Column(db.String(50), unique=True)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	email = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(80))
	posts = db.relationship('Post', backref='author', lazy=True)
	articles = db.relationship('Article', backref='author', lazy=True)
	journals = db.relationship('Journal', backref='author', lazy=True)
	notes  = db.relationship('Note', backref='author', lazy=True)
	subscriptions = db.relationship('Subscription', backref='author', lazy=True)
	subscribers = db.relationship('Subscriber', backref='author', lazy=True)



	def get_reset_token(self, expires_sec=3600):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)




class Post(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Article(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Journal(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Note(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Subscription(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	firstname = db.Column(db.String(20))
	lastname = db.Column(db.String(20))
	username = db.Column(db.String(50))
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Subscriber(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	firstname = db.Column(db.String(20))
	lastname = db.Column(db.String(20))
	username = db.Column(db.String(50))
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)




class Forum(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	firstname = db.Column(db.String(20))
	lastname = db.Column(db.String(20))
	username = db.Column(db.String(50))
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	fposts = db.relationship('Fpost', backref='author', lazy=True)





class Fpost(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	firstname = db.Column(db.String(20))
	lastname = db.Column(db.String(20))
	username = db.Column(db.String(50))
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'), nullable=False)

'''
class Freply(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'), nullable=False)
'''

