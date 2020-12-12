from flask import Blueprint, request, jsonify, render_template
from .drive import find_plagiarism, UnForgeInputError


plag_api  =Blueprint('Plagiarism Api', __name__)

@plag_api.route('/_unforge', methods = ['GET'])
def unforge_api_description():
	return render_template('api_description.html', api_post_url = request.url, prev_result = request.cookies.get('timestamp_id'))


@plag_api.route('/_unforge', methods = ['POST'])
def unforge_api():

	if 'language' not in request.form:
		return jsonify({'error':'language not added in form data'})

	if 'code_to_be_compared' not in request.files or 'code_compared_with' not in request.files:
		return jsonify({'error':'required files not found in posted data'})

	code_to_be_compared = request.files['code_to_be_compared']
	code1 = [str(i, 'utf-8') for i in code_to_be_compared.stream.readlines()]
	code1 = [(i+1, v) for i,v in enumerate(code1)]

	code_compared_with = request.files['code_compared_with']
	code2 = [str(i, 'utf-8') for i in code_compared_with.stream.readlines()]
	code2 = [(i+1, v) for i,v in enumerate(code2)]

	try:
		percentage, line_map, message, file_extension = find_plagiarism(request.form['language'], 
			code_to_be_compared.filename, code_compared_with.filename, code1, code2)
	except UnForgeInputError as e:
		return jsonify({'error':e})
	except Exception as e:
		print(e)
		return jsonify({'error':"Sorry :( Some internal error occured. It will be fixeed shortly" + str(e) })


	return jsonify({
		'percentage':percentage,
		'line_map': {str(i):str(v) for i,v in line_map.items()},
		'message':message or 'Thanks for using UnForge. Please write your review in the website :).'
		})