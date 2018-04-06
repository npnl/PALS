import os
from shutil import copyfile, rmtree

from commands import Commands

class Operations(object):
	def __init__(self, controller):
		self.controller = controller
		self.logger = controller.logger
		self.com = Commands(controller.logger)

		self.initialiseConstants()

	def initialiseConstants(self):
		self.subjects = []
		self.input_directory = self.controller.sv_input_dir.get()
		self.output_directory = self.controller.sv_output_dir.get()
		self.output_directories = []

		self.INTERMEDIATE_FILES = 'Intermediate_Files'
		self.ORIGINAL_FILES = 'Original_Files'


	def initialise(self):
		self.skip = False
		self.createOutputSubjectDirectories(self.input_directory, self.output_directory)
		self.runGzip()
		self.normaliseT1Intensity(self.controller.sv_t1_id.get())
		self.processLesionFilesForAll()

	def subjectPath(self, subject):
		return os.path.join(self.output_directory, subject)

	def intermediatePath(self, subject):
		return os.path.join(self.subjectPath(subject), self.INTERMEDIATE_FILES)

	def originalPath(self, subject):
		return os.path.join(self.intermediatePath(subject), self.ORIGINAL_FILES)

	def _copyDirectories(self, source_dir, dest_dir):
		for item in os.listdir(source_dir):
			if os.path.isdir(os.path.join(source_dir, item)):
				os.makedirs(os.path.join(dest_dir, item))
				self._copyDirecories(os.path.join(source_dir, item), os.path.join(dest_dir, item))
			else:
				copyfile(os.path.join(source_dir, item), os.path.join(dest_dir, item))

	def _createOriginalFiles(self, source_dir, target_dir):
		target_dir = os.path.join(target_dir, self.INTERMEDIATE_FILES, self.ORIGINAL_FILES)
		os.makedirs(target_dir)
		self._copyDirectories(source_dir, target_dir)

	def runGzip(self):
		if self.skip: return False
		for subject in self.subjects:
			directory = self.originalPath(subject)
			self.com.runGzip(directory)

	def _processLesionFilesForSubject(self, subject):
		subject_dir = self.originalPath(subject)
		counter = 1
		lesion_mask_id = self.controller.sv_lesion_mask_id.get()
		for item in os.listdir(subject_dir):
			if lesion_mask_id in item:
				lesion_file_path = os.path.join(subject_dir, item)
				output_bin_path = os.path.join(self.intermediatePath(subject), subject + '_' + lesion_mask_id + str(counter) + '_bin.nii.gz')
				self.com.runFslmathsOnLesionFile(lesion_file_path, output_bin_path)
				counter += 1

	def processLesionFilesForAll(self):
		if self.skip: return False
		for subject in self.subjects:
			self._processLesionFilesForSubject(subject)

	def _normaliseSubject(self, arg_1, arg_2, arg_3):
		minimum, maximum = self.com.runFslStat(arg_1)
		scaling = 255.0/(maximum - minimum)
		self.com.runFslMath(arg_1, minimum, scaling, os.path.join(arg_3, arg_2))

	def normaliseT1Intensity(self, t1_identifier):
		if self.skip: return False
		for subject in self.subjects:
			arg_1 = os.path.join(self.originalPath(subject), subject + '*' + t1_identifier + '*.nii.gz')
			arg_2 = subject + '_' + t1_identifier
			arg_3 = os.path.join(self.intermediatePath(subject))
			self._normaliseSubject(arg_1, arg_2, arg_3)

	def createOutputSubjectDirectories(self, base_input_directory, base_output_directory):
		if self.skip: return False
		all_input_directories = os.listdir(base_input_directory)
		for directory in all_input_directories:
			if os.path.isdir(os.path.join(base_input_directory, directory)):
				self.subjects.append(directory)
				output_directory = os.path.join(base_output_directory, directory)
				if os.path.exists(output_directory):
					rmtree(output_directory)
				os.makedirs(output_directory)
				input_directory = os.path.join(base_input_directory, directory)
				self._createOriginalFiles(input_directory, output_directory)

	def _getPathOfFiles(self, base_path, startswith_str='', substr='', endswith_str=''):
		all_files = []
		for item in os.listdir(base_path):
			if item.startswith(startswith_str) and substr in item and item.endswith(endswith_str):
				all_files.append(os.path.join(base_path, item))
		return all_files


	def setSubjectSpecificPaths(self, subject):
		if self.skip: return False
		anatomical_file_path = ''
		lesion_files = []

		anatomical_id = self.controller.sv_t1_id.get()
		intermediate_path = self.intermediatePath(subject)
		if 'unknown variable' == 'run_data_reorient': # Need to fix this
			params = (subject, anatomical_id, '_intNorm.nii.gz')
			anatomical_file_path = self._getPathOfFiles(intermediate_path, *params)[0]
			
			if anatomical_id == 'WMAdjusted':
				params = (subject, anatomical_id, 'bin.nii.gz')
				lesion_files = self._getPathOfFiles(self.subjectPath(subject), *params)
			else:
				params = (subject, anatomical_id, 'bin.nii.gz')
				lesion_files = self._getPathOfFiles(intermediate_path, *params)

		else:
			anatomical_file_path=os.path.join(self.subjectPath(subject), subject + '_' + anatomical_id + '_rad_reorient.nii.gz')
			if self.controller.b_wm_correction.get() or self.controller.b_ll_correction.get():
				if lesion_mask_id == 'WMAdjusted':
					params = (subject, anatomical_id, 'bin.nii.gz')
					lesion_files = self._getPathOfFiles(self.subjectPath(subject), *params)
				else:
					params = (subject, anatomical_id, 'rad_reorient.nii.gz')
					lesion_files = self._getPathOfFiles(intermediate_path, *params)
			else:
				params = (subject, anatomical_id, 'rad_reorient.nii.gz')
				lesion_files = self._getPathOfFiles(self.subjectPath(subject), *params)

		
		# if anatomical_file_path == '':
		# 	self.logger.info('Anatomical file not present. \
		# 						Make sure a with name like [%s*%s*_%s] \
		# 						is present in %s'%(params[0], params[1], params[2], intermediate_path))

		return anatomical_file_path, lesion_files



	def runBrainExtraction(self):
		if self.skip: return False
		if self.controller.b_brain_extraction.get() == False or self.skip: return False
		for subject in self.subjects:
			pass

	def getTemplateBrainROIS(self):
		parent_dir =  os.path.abspath(os.path.join(os.getcwd(), os.pardir))
		template_roi_dir = os.path.join(parent_dir, 'ROIs')
		template_rois = None
		for item in os.listdir(template_roi_dir):
			if item.startswith('MNI152_T1_2mm_brain'):
				template_rois = os.path.join(template_roi_dir, item)
				break
		return template_rois

def isValidPath(filePath):
	if os.path.exists(filePath):
		pass
	elif os.access(os.path.dirname(filePath), os.W_OK):
		pass
	else:
		return False
	return True

if __name__ == '__main__':
	pass

