import os
import ntpath
import pathlib

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
	output += 'background-color: black;' + '\n'
	output += 'max-width: 800px;' + '\n'
	output += 'margin: auto;' + '\n'
	output += '}' + '\n'

	output += 'button[type=button] {' + '\n'
	output += 'width: 20em; height: 3em;' + '\n'
	output += '}' + '\n'

	output += '.container {' + '\n'
	output += 'height: 340px;' + '\n'
	output += 'overflow: hidden;' + '\n'
	output += '}' + '\n'

	output += '.container img {' + '\n'
	output += ' margin-top: -120px;' + '\n'
	output += '}' + '\n'
	output += '</style>' + '\n'

	output += """<script language="Javascript" >

					function markSubject(subject_id){
						var sub_check_box = document.getElementById(subject_id);
						sub_check_box.checked = ! sub_check_box.checked;
					};

					function download(filename) {
					  var all_checked_boxes = document.getElementsByClassName('subject_checkbox');
					  var subjects_passed = ''
					  for(var i = 0; i < all_checked_boxes.length; i++){
					  	if(all_checked_boxes[i].checked === true){
					  		subjects_passed += all_checked_boxes[i].value + '\\n';
					  	}
					  }

					  var pom = document.createElement('a');
					  pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(subjects_passed));
					  pom.setAttribute('download', filename);

					  pom.style.display = 'none';
					  document.body.appendChild(pom);

					  pom.click();

					  document.body.removeChild(pom);
					}
					</script>"""

	output += '</head>' + '\n'
	output += '<body>' + '\n'
	output += """<FONT COLOR=WHITE FACE="Geneva, Arial" SIZE=7> QC Helper </FONT> <br>
	<FONT COLOR=WHITE FACE="Geneva, Arial" SIZE=4> Instructions: Use this page to visually inspect outputs for each subject. Only check 'Flag subject' if the subject data output does not meet acceptable standards. </br>When you arrive at the bottom of the page, click on 'Submit'. This will create a textfile containing the subjects that you have flagged. <br> After visual inspection, return to the PALS GUI. If you wish to omit subjects that do not pass inspection, click on 'Omit flagged subjects' and locate the path to the downloaded flagged subjects file. </FONT><br><br>

	"""

	output += """<form onsubmit="download('selected_subjects.txt')">""" + '\n'

	image_files = _getPathOfFiles(images_dir, endswith_str='.png')
	image_files.sort()
	for image_path in image_files:
		image_name = _extractFileName(image_path)
		subject = image_name.split('_')[0]

		if page_type == 'Lesions':
			lesion_num = image_name.split('_')[1]

		output += '<table cellspacing="1" style="width:100%; background-color:#000;">' + '\n'
		output += '<tr>' + '\n'
		output += '<td> <FONT COLOR=WHITE FACE="Geneva, Arial" SIZE=5> %s </FONT> </td>'%(subject) + '\n'
		output += '</tr>' + '\n'


		if page_type == 'Lesions':
			output += '<tr>' + '\n'
			output += """<td><FONT COLOR=WHITE FACE="Geneva, Arial" SIZE=3> %s </FONT><div class="container"><img src="%s" height="600" onclick="markSubject('%s')"></div>"""%(lesion_num, _extractFileName(image_path, remove_extension=False), subject) + '\n'
			output += '<center><input id="%s" class="subject_checkbox" type="checkbox" name="status" value="%s"><FONT COLOR=WHITE SIZE=3 FACE="Geneva, Arial"> Flag subject</FONT></center><br><br></td>'%(subject, subject) + '\n'
		else:
			output += '<tr>' + '\n'
			output += """<td><div class="container"><img src="%s" height="600" onclick="markSubject('%s')"></div>"""%(_extractFileName(image_path, remove_extension=False), subject) + '\n'
			output += '<center><input id="%s" class="subject_checkbox" type="checkbox" name="status" value="%s"><FONT COLOR=WHITE SIZE=3 FACE="Geneva, Arial"> Flag subject</FONT></center><br><br></td>'%(subject, subject) + '\n'

		output += '</table>' + '\n'
	output += """<button type="button" class="btn" onclick="download('selected_subjects.txt')">Submit</button><br></br>""" + '\n'
	output += '</form>' + '\n'
	output += '</body>' + '\n'
	output += '</html>\n' + '\n'

	html_file_path = os.path.join(images_dir, page_type + '.html')

	with open(html_file_path, 'w') as f:
		f.write(output)
		f.close()

	return pathlib.Path(html_file_path).as_uri()

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
