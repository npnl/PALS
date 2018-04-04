import os
from shutil import copyfile, rmtree

def isValidPath(filePath):
	if os.path.exists(filePath):
		pass
	elif os.access(os.path.dirname(filePath), os.W_OK):
		pass
	else:
		return False
	return True



# BASE_DIRECTORY = os.path.join(os.getcwd(), 'data')

def copyDirectories(source_dir, dest_dir):
	for item in os.listdir(source_dir):
		if os.path.isdir(os.path.join(source_dir, item)):
			os.makedirs(os.path.join(dest_dir, item))
			copyDirecories(os.path.join(source_dir, item), os.path.join(dest_dir, item))
		else:
			copyfile(os.path.join(source_dir, item), os.path.join(dest_dir, item))

def createOriginalFiles(source_dir, target_dir):
	target_dir = os.path.join(target_dir, 'Intermediate_Files/Original_Files')
	os.makedirs(target_dir)
	copyDirectories(source_dir, target_dir)

def createOutputSubjectDirectories(base_input_directory, base_output_directory, identifier):
	all_input_directories = os.listdir(base_input_directory)
	input_directories = []
	for directory in all_input_directories:
		print directory
		if os.path.isdir(os.path.join(base_input_directory, directory)) and directory.startswith(identifier):
			input_directories.append(directory)
			output_directory = os.path.join(base_output_directory, directory)
			if os.path.exists(output_directory):
				shutil.rmtree(output_directory)
			os.makedirs(output_directory)
			input_directory = os.path.join(base_input_directory, directory)
			createOriginalFiles(input_directory, output_directory)