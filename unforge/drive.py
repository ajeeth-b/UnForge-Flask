from .unforge_plag import main

class UnForgeInputError(Exception):
	pass

def verifyInput(args):

	lang = (args['l'].strip()).lower()
	file_extension = None
	if   'js'   == lang or 'javascript' == lang:
		args['l'] = 'JavaScript'
		file_extension = '.js'
	elif 'py'   == lang or 'python' == lang or 'python3' == lang:
		args['l'] = 'Python3'
		file_extension = '.py'
	elif 'cpp'  == lang or 'c++' == lang:
		args['l'] = 'CPP14'
		file_extension = '.cpp'
	elif 'java' == lang:
		args['l'] = 'Java9'
		file_extension = '.java'
	elif 'c'    == lang:
		args['l'] = 'C'
		file_extension = '.c'
	else:
		raise UnForgeInputError('No such language is supported in UnForge :(')

	if not args['f1_name'].endswith(file_extension):
		raise UnForgeInputError('Please provide ' + file_extension + ' files as input')

	if args['f1_name'].split('.')[-1] != args['f2_name'].split('.')[-1]:
		raise UnForgeInputError('Please provide ' + file_extension + ' files as input')
	return file_extension


def find_plagiarism(language, file1, file2, code1, code2):
	args = {'l':language,'f1_name':file1, 'f2_name':file2, 'f1':code1, 'f2':code2}
	file_extension = verifyInput(args)
	percentag, line_map, message = main(args)
	return (percentag, line_map, message, file_extension)
