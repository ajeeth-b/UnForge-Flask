from flask import Blueprint, render_template, request, current_app as app, make_response
import os
from .drive import find_plagiarism, UnForgeInputError
from datetime import datetime, timedelta
import json
from boto3.dynamodb.conditions import Key
from .db_init import data_table, review_table, _save_space
from .decorators import login_required

plag = Blueprint('Plagiarism', __name__)

@plag.route('/find_plagiarism/')
def detect_with_file():
	return render_template('plagiarism/file_upload.html', prev_result = request.cookies.get('timestamp_id'))

@plag.route('/result', methods = ['POST'])
def find_plagiarism_for_code():
	language = request.form['language']
	timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S-%f")
	
	code1 = request.files['code1']
	code1_lines = [str(i, 'utf-8') for i in code1.stream.readlines()]
	code1_content = [(i+1, v) for i,v in enumerate(code1_lines)]

	code2 = request.files['code2']
	code2_lines = [str(i, 'utf-8') for i in code2.stream.readlines()]
	code2_content = [(i+1, v) for i,v in enumerate(code2_lines)]

	try:
		percentage, line_map, message, file_extension = find_plagiarism(language, 
			code1.filename, code2.filename, code1_content, code2_content)
	except UnForgeInputError as e:
		return '<br>selected language : ' + language + '<br><br>File to be compared : ' + code1.filename + \
		'<br><br>File compared with : ' + code2.filename +'<br><br>Your input is incorrect.<br><br><h3>' +str(e)
	except Exception as e:
		print(e)
		return "Sorry :( <br>Some internal error occured. It will be fixeed shortly<br><br><br>" + str(e) 

	old_timestamp = request.cookies.get('timestamp_id')
	try:
		item = {
			'timestamp':timestamp,
			'language':file_extension,
			'percentage' : percentage,
			'line_map':{str(i):str(j) for i,j in line_map.items()} ,
			'message':message, 
			'code1_name': code1.filename,
			'code2_name': code2.filename,
			'code1':code1_lines,
			'code2':code2_lines
		}
		if not _save_space:
			item['previous'] = old_timestamp
		data_table.put_item(Item = item)
	except Exception as e:
		print(e)

	response = make_response(render_template('plagiarism/result.html', file1_name = code1.filename, file2_name = code2.filename,
		percent = percentage, message = message, code1 = code1_content, code2 = code2_content,
		code1_hilights = line_map.keys(), code2_hilights = line_map.values(),
		prev_result = request.cookies.get('timestamp_id'))
		)
	if old_timestamp:
		has_review = review_table.query(
			KeyConditionExpression=Key('timestamp').eq(old_timestamp)
			)
		if not has_review['Items'] and _save_space:
			data_table.delete_item(Key = {'timestamp':old_timestamp})
	response.set_cookie('timestamp_id', timestamp)
	return response


@plag.route('/result/', methods = ['GET'])
@login_required
def show_plagiarism_result():
	timestamp = request.cookies.get('timestamp_id')
	if timestamp is None:
		response = make_response(render_template('failed_page.html'))
		response.set_cookie('timestamp_id','', max_age = 0)
		return response

	result = data_table.query(
		KeyConditionExpression=Key('timestamp').eq(timestamp)
		)

	if not result['Items']:
		response = make_response(render_template('failed_page.html'))
		response.set_cookie('timestamp_id','', max_age = 0)
		return response

	result = result['Items'][0]

	code1_content = [(i+1, v) for i,v in enumerate(result['code1'])]
	code2_content = [(i+1, v) for i,v in enumerate(result['code2'])]

	return render_template('plagiarism/result.html', file1_name = result['code1_name'], file2_name = result['code2_name'],
		percent = result['percentage'], message = result['message'], code1 = code1_content, code2 = code2_content,
		code1_hilights = [int(i) for i in result['line_map'].keys()], code2_hilights = [int(i) for i in result['line_map'].values()])