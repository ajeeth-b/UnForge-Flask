from flask import Flask, render_template, request
import os

def create_app():
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_pyfile('config.py')
	
	@app.route('/')
	def main():
		return render_template('index.html', prev_result = request.cookies.get('timestamp_id'))

	with app.app_context():

		try:
			from . import db_init
		except Exception as e:
			print('Error in connecting DB:\n\n',e)
			return None

		from .plagiarism import plag
		app.register_blueprint(plag)

		from .plagiarism_api import plag_api
		app.register_blueprint(plag_api)

		from .review import review
		app.register_blueprint(review)

		from .authentication import auth
		app.register_blueprint(auth)

	return app
