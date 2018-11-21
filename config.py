import os
import ConfigParser

basedir = os.path.abspath(os.path.dirname(__file__))
# load up all the configs
config = ConfigParser.RawConfigParser()
config.read(basedir,'../conf/apikeys.conf')

class Config(object):
	DATABASE_URL 	= os.environ.get('DATABASE_URL') or 'mysql://192.168.1.100'
	DATABASE_NAME 	= os.environ.get('DATABASE_NAME') or 'alfr3d'
	DATABASE_USER 	= os.environ.get('DATABASE_USER') or 'alfr3d'
	DATABASE_PSWD 	= os.environ.get('DATABASE_PSWD') or 'alfr3d'
