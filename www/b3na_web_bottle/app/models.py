from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	about_me = db.Column(db.String(140))
	last_online = db.Column(db.DateTime, index=True, default=datetime.utcnow)	
	#state = db.Column(db.Integer, db.ForeignKey('states.id'))
	#location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
	user_type = db.Column(db.Integer, db.ForeignKey('user_types.id'))
	environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'))

	# Note: relationship is referenced by the model class --> Post
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	device = db.relationship('Device', backref='user', lazy='dynamic')

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)		

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
			digest, size)		

class UserTypes(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(16), index=True)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	# Note: relationship is referenced by the table name --> user
	# which is automatically in lowercase (thanks SQLAlchemy)
	# mutli-word model names become snake_case
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post {}>'.format(self.body)

class Device(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), index=True)
	IP = db.Column(db.String(24))
	MAC = db.Column(db.String(24), unique=True)
	state_id = db.Column(db.Integer, db.ForeignKey('states.id'))
	last_online = db.Column(db.DateTime, default=datetime.utcnow, index=True)	
	device_type_id = db.Column(db.Integer, db.ForeignKey('device_types.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'))

class DeviceTypes(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(16), index=True, unique=True)
	dev_type = db.relationship('Device', backref='device_type', lazy='dynamic')

class States(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	state = db.Column(db.String(10), default='offline', index=True, unique=True)
	dev_state = db.relationship('Device', backref='state', lazy='dynamic')

class Environment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), index=True)
	dev_env = db.relationship('Device', backref='environment', lazy='dynamic')
	usr_env = db.relationship('User', backref='environment', lazy='dynamic')

class Location(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	latitude = db.Column(db.DECIMAL(6,4))
	longitude = db.Column(db.DECIMAL(6,4))
	country = db.Column(db.String(24))
	state = db.Column(db.String(24))
	city = db.Column(db.String(24))
	IP = db.Column(db.String(24))
	environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'))

class Weather(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	low = db.Column(db.Integer)
	high = db.Column(db.Integer)
	description = db.Column(db.String(64))
	sunrise = db.Column(db.DateTime)
	sunset = db.Column(db.DateTime)
	environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'))

@login.user_loader
def load_user(id):
	return User.query.get(int(id))