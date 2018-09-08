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