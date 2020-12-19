from flask import Blueprint, render_template, request, session, redirect, flash
from boto3.dynamodb.conditions import Key
from .db_init import user_table
from .decorators import login_required

auth = Blueprint('Authentication', __name__)


@auth.route('/signup/', methods = ['GET'])
def get_signup_page():
	return render_template('authentication/signup_login.html')

@auth.route('/login/', methods = ['GET'])
def get_login_page():	
	return render_template('authentication/signup_login.html', login = "active" )

def create_session(user):
	del user['password']
	session['logged_in'] = True
	session['user'] = user

def delete_session():
	session.pop('logged_in', None)
	session.pop('user',None)
	session.clear()


@auth.route('/signup', methods = ['POST'])
def signup():
	delete_session()

	if not all([i in request.form for i in ['email','name','password']]):
		flash("Please fill all the feilds.",'signup-error')
		return render_template('authentication/signup_login.html')


	result = user_table.query(
		KeyConditionExpression=Key('mail').eq(request.form['email'])
		)
	if result['Items']:
		flash('User alredy exist.Please login.','login-error')
		return render_template('authentication/signup_login.html', login='active')


	user_item = {
	'mail':request.form['email'],
	'first_name':request.form['name'],
	'password':request.form['password'],
	'usage_id':[]
	}
	user_table.put_item(Item = user_item)

	create_session(user_item)
	return redirect('/find_plagiarism')



@auth.route('/login', methods = ['POST'])
def login():
	delete_session()

	if 'email' not in request.form or 'password' not in request.form:
		flash('Please fill all the fields.','login-error')
		return render_template('authentication/signup_login.html', login='active')

	result = user_table.query(
		KeyConditionExpression=Key('mail').eq(request.form['email'])
		)
	if not result['Items']:
		flash('No such user in UnForge. Please signup.','signup-error')
		return render_template('authentication/signup_login.html')

	user  = result['Items'][0]
	if user['password'] != request.form['password']:
		flash('Incorrect Password.','login-error')
		return render_template('authentication/signup_login.html', login='active')
	create_session(user)
	return redirect('/find_plagiarism')


@auth.route('/logout/')
@login_required
def logout():
	delete_session()
	return redirect('/')

@auth.route('/ses/')
@login_required
def ses():
	return f'''logged_in : ''' + str(session['logged_in']) +  '\nUser : ' + str(session['user'])


