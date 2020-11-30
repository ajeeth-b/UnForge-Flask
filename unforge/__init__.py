from flask import Flask, render_template, request
import os

def create_app():
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_pyfile('config.py')

	@app.route('/')
	def main():
		return render_template('index.html', prev_result = request.cookies.get('timestamp_id'))

	with app.app_context():
		from .plagiarism import plag
		app.register_blueprint(plag)

	return app
