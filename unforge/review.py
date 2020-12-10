from flask import Blueprint, render_template, request
from .db_init import review_table
from datetime import datetime

review = Blueprint("Review", __name__)

@review.route('/review')
def review_page():
	return render_template('review.html', prev_result = request.cookies.get('timestamp_id'))

@review.route('/review', methods = ['POST'])
def get_review():
	timestamp = request.cookies.get('timestamp_id')

	if not timestamp:
		timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S-%f")
	item = {'timestamp': timestamp, 'review':request.form['review']}
	if request.form['name']:
		item['name'] = request.form['name']
	if request.form['email']:
		item['email'] = request.form['email']
	review_table.put_item(Item = item)

	return render_template('review_thank.html', prev_result = request.cookies.get('timestamp_id'))
