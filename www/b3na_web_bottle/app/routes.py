from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EditDeviceForm
from app.models import User, Device, DeviceTypes, States, Environment
from werkzeug.urls import url_parse
from datetime import datetime


@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
	posts = [
		{
			'author':{'username':'Alfr3d'},
			'status':'online and well'
		},
		{
			'author':{'username':'Armageddion'},
			'status':'doing cool stuff'
		}
	]

	devices = Device.query.all()

	return render_template('index.html', title='Home', posts=posts, devices=devices)

@app.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)

	return render_template('login.html', title='Sign in', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))

	return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	posts = [
		{'author': user, 'body': 'Test post #1'},
		{'author': user, 'body': 'Test post #2'}
	]
	devices = Device.query.filter_by(user_id=user.id)
	return render_template('user.html', title=user.username, user=user, posts=posts, devices=devices)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile',
						   form=form, user=current_user)

@app.route('/device/<mac>', methods=['GET', 'POST'])
@login_required
def edit_device(mac):
	device = Device.query.filter_by(MAC=mac).first()
	device_types = DeviceTypes.query.all()
	users = User.query.all()
	environments = Environment.query.all()
	form = EditDeviceForm()
	if form.validate_on_submit():
		device.device_type_id=DeviceTypes.query.filter_by(type=request.form['types']).first().id
		device.user_id=User.query.filter_by(username=request.form['users']).first().id
		device.name=form.name.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('index'))
	elif request.method == 'GET':
		form.name.data = device.name
	return render_template('edit_device.html', \
							title='Edit Device', \
							form=form, \
							device=device, \
							device_types=device_types, \
							users=users, \
							environments=environments)
