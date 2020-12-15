from flask import render_template, session, flash
from functools import wraps

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		print(session)
		if 'logged_in'in session and session['logged_in'] :
			return f(*args, **kwargs)
		flash('Please Login to view.','login-required')
		return render_template('authentication/signup_login.html', login="active")
	return wrap