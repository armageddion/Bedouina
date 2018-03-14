# remember to set env var FLASK_APP to b3na.py 
# nix: export FLASK_APP=b3na.py
# win: set FLASK_APP=b3na.py

from app import app, db
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
	return {'db':db, 'User':User, 'Post':Post}