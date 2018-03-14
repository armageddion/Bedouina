import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	# Flask-WTF extension uses this to protect web forms against Cross-Site Request Forgery or CSRF 
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

	# Flask-SQLAlchemy uses this stuff
	# SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
	# 						'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_DATABASE_URI = 'mysql://alfr3d:alfr3d@10.0.0.69/alfr3d'

	SQLALCHEMY_TRACK_MODIFICATION = False