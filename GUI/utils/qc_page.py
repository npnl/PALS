import os
import ntpath

def _getPathOfFiles(base_path, endswith_str=''):
	all_files = []
	for item in os.listdir(base_path):
		if item.endswith(endswith_str):
			all_files.append(os.path.join(base_path, item))
	return all_files

def _extractFileName(path, remove_extension=True):
	head, tail = ntpath.split(path)
	filename =  tail or ntpath.basename(head)
	if remove_extension:
		filename, file_extension = os.path.splitext(filename)
	return filename


def generateQCPage(page_type, images_dir):
	output = ''
	output += '<html>' + '\n'
	output += '<head>'  + '\n'
	output += '<style type="text/css">' + '\n'
	output += '*' + '\n'
	output += '{'  + '\n'
	output += 'margin: 0px;' + '\n'
	output += 'padding: 0px;'  + '\n'
	output += '}' + '\n'
	output += 'html, body'  + '\n'
	output += '{' + '\n'
	output += 'height: 100%;' + '\n'
	output += '}' + '\n'

	output += '.container {' + '\n'
	output += 'height: 240px;' + '\n'
	output += 'overflow: hidden;' + '\n'
	output += '}' + '\n'

	output += '.container img {' + '\n'
	output += ' margin-top: -200px;' + '\n'
	output += '}' + '\n'
	output += '</style>' + '\n'
	output += '</head>' + '\n'
	output += '<body>' + '\n'


	image_files = _getPathOfFiles(images_dir, endswith_str='.png')
	for image_path in image_files:
		image_name = _extractFileName(image_path)
		subject = image_name.split('_')[0]

		if page_type == 'lesion':
			lesion_num = image_name.split('_')[1]

		output += '<table cellspacing="1" style="width:100%; background-color:#000;">' + '\n'
		output += '<tr>' + '\n'
		output += '<td> <FONT COLOR=WHITE FACE="Geneva, Arial" SIZE=5> %s </FONT> </td>'%(subject) + '\n'
		output += '</tr>' + '\n'
		
		if page_type == 'lesion':
			output += '<tr>' + '\n'
			output += '<td><FONT COLOR=WHITE FACE="Geneva, Arial" SIZE=3> %s </FONT><div class="container"><a href="file:%s"><img src="%s" height="600" ></a></div></td>'%(lesion_num, image_path, image_path) + '\n'
		else:
			output += '<tr>' + '\n'
			output += '<td><div class="container"><a href="file:%s"><img src="%s" height="600" ></a></div></td>'%(image_path, image_path) + '\n'
	
		output += '</table>' + '\n'
	
	output += '</body>' + '\n'
	output += '</html>\n' + '\n'

	with open(os.path.join(images_dir, page_type + '.html'), 'w') as f:
		f.write(output)
		f.close()
