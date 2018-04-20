class BaseOperation():

	def getBaseDirectory(self):
		return self.output_directory

	def getSubjectPath(self, subject):
		return os.path.join(self.output_directory, subject)

	def getIntermediatePath(self, subject):
		return os.path.join(self.getSubjectPath(subject), self.INTERMEDIATE_FILES)

	def getOriginalPath(self, subject):
		return os.path.join(self.getIntermediatePath(subject), self.ORIGINAL_FILES)

	def _getPathOfFiles(self, base_path, startswith_str='', substr='', endswith_str='', second_sub_str=''):
		all_files = []
		for item in os.listdir(base_path):
			if item.startswith(startswith_str) and substr in item and second_sub_str in item and item.endswith(endswith_str):
				all_files.append(os.path.join(base_path, item))
		return all_files